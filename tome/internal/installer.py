import fnmatch
import json
import os
import platform
import shutil
import sys
import tarfile
import tempfile
import venv
import zipfile
from contextlib import contextmanager
from datetime import datetime
from io import StringIO
from urllib.parse import urlparse

from tome.api.output import TomeOutput
from tome.errors import TomeException
from tome.internal.cache import TomePaths
from tome.internal.source import SourceType
from tome.internal.utils.files import chdir, save
from tome.internal.utils.files import copy_file
from tome.internal.utils.files import is_subdirectory
from tome.internal.utils.files import rmdir
from tome.internal.utils.network import FileDownloader
from tome.internal.utils.runners import detect_runner
from tome.internal.utils.runners import tome_run


class IgnoreMatcher:
    """Manage ignore patterns from a .tomeignore file."""

    def __init__(self, ignore_file):
        self.patterns = {".tomeignore"}
        if os.path.exists(ignore_file):
            with open(ignore_file) as file:
                for line in file:
                    content = line.split("#", 1)[0].strip()
                    if content:
                        self.patterns.add(content)

    def match(self, path):
        return any(fnmatch.fnmatch(path, pattern) for pattern in self.patterns)


def is_compressed_file(filepath):
    if any(filepath.endswith(ext) for ext in (".zip", ".tar.gz", ".tgz", ".tar.bz2", ".tar", ".gz", ".tar.xz")):
        return True
    return False


@contextmanager
def temporary_folder():
    tmp_dir = tempfile.mkdtemp()
    try:
        yield tmp_dir
    finally:
        rmdir(tmp_dir)


def clone_git_repo(source, destination):
    output = TomeOutput()
    with temporary_folder() as tmp_dir:
        with chdir(tmp_dir):
            clone_cmd = f"git clone \"{source.uri}\" ."
            checkout_cmd = f"git checkout {source.version}" if source.version else ""

            clone_message = (
                f"Cloning {source}" if not source.version else f"Cloning {source} at '{source.version}' branch"
            )
            output.info(clone_message)
            ret, out = detect_runner(clone_cmd)
            if ret != 0:
                raise TomeException(f"Failed to clone {source}: {out}")

            if checkout_cmd:
                ret, out = detect_runner(checkout_cmd)
                if ret != 0:
                    raise TomeException(f"Failed to checkout {source} at {source.version}: {out}")

            ret, out = detect_runner('git rev-list HEAD -n 1 --full-history')
            if ret != 0:
                raise TomeException(f"Cannot obtain commit information after clone: {out}")
            commit = out.strip()

            output.info(f"Cloned {source}")
            folder = os.path.join(tmp_dir, source.folder) if source.folder else tmp_dir

            if source.folder and not os.path.exists(folder):
                raise TomeException(f"Folder specified with --folder: '{source.folder}' does not exist after cloning.")

            process_folder(folder, destination)
    return commit


# TODO: this is not optimal, it would be better to only extract
#  the folder specified in the zip_folder
def unpack_file(path_to_file, zip_folder, destination):
    if zipfile.is_zipfile(path_to_file):
        with zipfile.ZipFile(path_to_file, 'r') as archive:
            archive.extractall(destination)
    elif tarfile.is_tarfile(path_to_file):
        with tarfile.open(path_to_file, 'r:*') as archive:
            archive.extractall(destination)
    else:
        raise TomeException(f"Unsupported file type: {path_to_file}")

    if zip_folder:
        folder = zip_folder.rstrip('/')
        folder_path = os.path.join(destination, folder)
        if not os.path.exists(folder_path):
            raise TomeException(f"Folder '{zip_folder}' not found in the archive.")

        for item in os.listdir(folder_path):
            src = os.path.join(folder_path, item)
            dst = os.path.join(destination, item)
            shutil.move(src, dst)
        os.rmdir(folder_path)


def process_folder(folder, destination):
    output = TomeOutput()
    ignore_file = os.path.join(folder, '.tomeignore')
    ignore_matcher = IgnoreMatcher(ignore_file)
    copied, ignored = 0, 0
    output.verbose(f"Copying files from {folder} to {destination}.")
    for root, dirs, files in os.walk(folder, topdown=True):
        dirs[:] = [d for d in dirs if not ignore_matcher.match(d) and d != ".git"]  # Filter directories
        for name in files:
            rel_path = os.path.relpath(os.path.join(root, name), folder)
            if not ignore_matcher.match(rel_path):
                source_file = os.path.join(root, name)
                _destination = os.path.join(destination, os.path.relpath(root, folder))
                copy_file(source_file, _destination)
                output.verbose(f"Copied {rel_path}")
                copied += 1
            else:
                output.verbose(f"Ignored {rel_path}", verbosity=TomeOutput.LEVEL_VV)
                ignored += 1

    output.info(f"Copied {copied} files. Ignored {ignored} files.")


def download_and_extract(source, destination):
    output = TomeOutput()
    filename = os.path.basename(urlparse(source.uri).path)
    destination_file = os.path.join(destination, filename)

    with temporary_folder() as tmp_dir:
        downloader = FileDownloader()
        filepath = os.path.join(tmp_dir, filename)
        downloader.download(source.uri, filepath, verify_ssl=source.verify_ssl)

        if is_compressed_file(destination_file):
            unpack_file(filepath, source.folder, destination)
            output.info(f"Extracted {destination_file}")
        else:
            output.warning(f"Downloaded {destination_file} but did not extract (unsupported type)")


def install_from_source(source, cache_destination_folder, force_requirements, create_env):
    if os.path.exists(cache_destination_folder):
        rmdir(cache_destination_folder)
    if source.type is SourceType.GIT:
        commit = clone_git_repo(source, cache_destination_folder)
        source.commit = commit
    elif source.type is SourceType.FOLDER:
        process_folder(source.uri, cache_destination_folder)
    elif source.type is SourceType.FILE:
        assert is_compressed_file(source.uri)
        with temporary_folder() as tmp_dir:
            with chdir(tmp_dir):
                unpack_file(source.uri, source.folder, tmp_dir)
                process_folder(source.uri, cache_destination_folder)
    elif source.type is SourceType.URL:
        download_and_extract(source, cache_destination_folder)

    tome_source = os.path.join(cache_destination_folder, "tome_source.json")
    save(tome_source, json.dumps(source.serialize(), indent=4))

    # The requirements.txt would have been copied to the folder
    _install_requirements(cache_destination_folder, force_requirements, create_env, origin=source)


def install_editable(source, cache_base_folder, force_requirements, create_env):
    """
    Updates the cache directory with a new source installed in editable mode.
    If an editable installations file doesn't exist, it creates a new one.

    :param create_env:
    :param force_requirements:
    :param source: The source of the scripts to be installed in editable mode.
    :param cache_base_folder: The cache directory where the installations file is stored.
    """
    output = TomeOutput()
    os.makedirs(cache_base_folder, exist_ok=True)

    _install_requirements(source.uri, force_requirements, create_env)

    editables_file = TomePaths(cache_base_folder).editables_path

    if os.path.exists(editables_file):
        with open(editables_file) as f:
            editable_sources = json.load(f)
    else:
        editable_sources = []

    if not any(editable['source'] == source.uri for editable in editable_sources):
        info = {"source": source.uri, "installed_on": datetime.now().timestamp()}
        editable_sources.append(info)

        with open(editables_file, 'w') as f:
            json.dump(editable_sources, f, indent=4)

        output.info(f"Configured editable installation for '{source.uri}'")
    else:
        output.info(f"The source '{source.uri}' is already configured as editable.")


def _install_requirements(source_dir, force_requirements, create_env, origin=None):
    reqs = os.path.join(source_dir, "requirements.txt")
    if not os.path.isfile(reqs):
        return

    output = TomeOutput()
    python_executable = sys.executable
    if create_env:
        # FIXME: We also have to install tome in this created environment
        # Create new environment
        env_path = os.path.join(source_dir, ".tome_venv")
        with TomeOutput.spinner("Creating virtual environment"):
            venv.create(env_path, with_pip=True)
        output.info(f"Created the virtual environment located at '{env_path}'")
        python_executable = (
            os.path.join(env_path, "Scripts", "python.exe")
            if platform.system() == "Windows"
            else os.path.join(env_path, "bin", "python")
        )
    elif not force_requirements:
        in_virtualenv = (
            hasattr(sys, 'real_prefix')
            or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
            or 'VIRTUAL_ENV' in os.environ
        )
        if not in_virtualenv:
            raise TomeException(
                "You must be within a virtual environment to install requirements or use the --create-env argument."
            )

    env_message = "created" if create_env else "current"
    output.info(
        f"Scripts from {origin.url if origin else source_dir} contain a 'requirements.txt', installing it in the {env_message} virtual environment."
    )

    command = f"\"{python_executable}\" -m pip install -r \"{reqs}\""
    try:
        with TomeOutput.spinner("Installing requirements"):
            code = tome_run(command, cwd=source_dir)
        output.info(f"Successfully installed requirements from {reqs}")
    except TomeException as e:
        raise TomeException(f"pip install failed. These commands might not work correctly: {e}") from None
    if code != 0:
        raise TomeException("pip install failed. These commands might not work correctly.")


def uninstall_from_source(source, cache_base_folder, cache_remove_folder):
    """
    Uninstalls a source from the cache directory. If the source is installed in editable mode,
    it removes it from the editable installations list. Otherwise, it removes the source's
    directory from the cache.

    :param source: The source of the scripts to be uninstalled.
    :param cache_base_folder: The base folder for the cache.
    :param cache_remove_folder: The cache directory where the installations are stored.
    """
    output = TomeOutput()
    editables_file = TomePaths(cache_base_folder).editables_path

    # Check if the source is in editable installations
    if os.path.exists(editables_file) and os.path.isdir(os.path.abspath(source)):

        def is_editable(editablepath, editablesources):
            for editable in editablesources:
                if 'source' in editable and os.path.abspath(editable['source']) == editablepath:
                    return True

        editable_path = os.path.abspath(source)
        with open(editables_file) as f:
            editable_sources = json.load(f)

        if is_editable(editable_path, editable_sources):
            editable_sources = [editable for editable in editable_sources if editable['source'] != editable_path]
            with open(editables_file, 'w') as f:
                json.dump(editable_sources, f, indent=4)
            output.info(f"Removed '{source}' from editable installations.")
            return

    # If the source is not editable, attempt to remove the source directory from cache
    if os.path.isdir(cache_remove_folder):
        # Additional safety checks
        if not is_subdirectory(cache_remove_folder, cache_base_folder):
            raise TomeException(f"Attempted to uninstall from outside the cache directory: {cache_remove_folder}")

        if os.path.samefile(cache_remove_folder, cache_base_folder):
            raise TomeException("Attempted to uninstall the entire cache base folder, operation cancelled.")

        rmdir(cache_remove_folder)
        output.info(f"Uninstalled '{source}' and removed directory: {cache_remove_folder}")
    else:
        raise TomeException(f"Source '{source}' is not installed or already uninstalled.")
