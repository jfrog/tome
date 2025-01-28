import hashlib
import os
import platform
import shutil
import stat
import time
from contextlib import contextmanager
from pathlib import Path

from tome.errors import TomeException


def _change_permissions(func, path, exc_info):
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise OSError(f"Cannot change permissions for {path}! Exception info: {exc_info}")


if platform.system() == "Windows":

    def rmdir(path):
        if not os.path.isdir(path):
            return

        retries = 3
        delay = 0.5
        for i in range(retries):
            try:
                shutil.rmtree(path, onerror=_change_permissions)
                break
            except OSError as err:
                if i == retries - 1:
                    raise TomeException(
                        f"Couldn't remove folder: {path}\n{err!s}\n"
                        "Folder might be busy or open. "
                        "Close any app using it and retry."
                    ) from err
                time.sleep(delay)

    def renamedir(old_path, new_path):
        retries = 3
        delay = 0.5
        for i in range(retries):
            try:
                shutil.move(old_path, new_path)
                break
            except OSError as err:
                if i == retries - 1:
                    raise TomeException(
                        f"Couldn't move folder: {old_path}->{new_path}\n"
                        f"{err!s}\n"
                        "Folder might be busy or open. "
                        "Close any app using it and retry."
                    ) from err
                time.sleep(delay)
else:

    def rmdir(path):
        if not os.path.isdir(path):
            return
        try:
            shutil.rmtree(path, onerror=_change_permissions)
        except OSError as err:
            raise TomeException(
                f"Couldn't remove folder: {path}\n{err!s}\n"
                "Folder might be busy or open. "
                "Close any app using it and retry."
            ) from err

    def renamedir(old_path, new_path):
        try:
            shutil.move(old_path, new_path)
        except OSError as err:
            raise TomeException(
                f"Couldn't move folder: {old_path}->{new_path}\n{err!s}\n"
                "Folder might be busy or open. "
                "Close any app using it and retry."
            ) from err


@contextmanager
def chdir(newdir):
    old_path = os.getcwd()
    os.chdir(newdir)
    try:
        yield
    finally:
        os.chdir(old_path)


def sha1(value: str):
    if value is None:
        return None
    md = hashlib.sha1()
    md.update(value)
    return md.hexdigest()


def sha256(value):
    if value is None:
        return None
    md = hashlib.sha256()
    md.update(value)
    return md.hexdigest()


def short_hash_path(h):
    """:param h: Text to reduce"""
    h = h.encode("utf-8")
    md = hashlib.sha256()
    md.update(h)
    sha_bytes = md.hexdigest()
    return sha_bytes[0:13]


def _generic_algorithm_sum(file_path, algorithm_name):
    with open(file_path, 'rb') as fh:
        try:
            m = hashlib.new(algorithm_name)
        except ValueError:
            m = hashlib.new(algorithm_name, usedforsecurity=False)
        while True:
            data = fh.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()


def copy_file(source_file, destination_dir):
    """
    Copies a file from 'source_file' to the 'destination_dir' folder.
    Creates the destination folder if it doesn't exist.

    :param source_file: Absolute path to the source file.
    :param destination_dir: Absolute path to the destination folder.
    """
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir, exist_ok=True)

    destination_file = os.path.join(destination_dir, os.path.basename(source_file))

    shutil.copy2(source_file, destination_file)


def check_with_algorithm_sum(algorithm_name, file_path, signature):
    real_signature = _generic_algorithm_sum(file_path, algorithm_name)
    if real_signature != signature.lower():
        raise TomeException(
            f"{algorithm_name} signature failed for '{os.path.basename(file_path)}' file. \n"
            f" Provided signature: {signature}  \n"
            f" Computed signature: {real_signature}"
        )


def save(path, content, encoding="utf-8"):
    """
    Saves a file with given content
    Params:
        path: path to write file to
        content: contents to save in the file
        encoding: target file text encoding
    """

    dir_path = os.path.dirname(path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    with open(path, "w", encoding=encoding, newline="") as handle:
        handle.write(content)


def save_files(path, files, encoding="utf-8"):
    for name, content in files.items():
        save(os.path.join(path, name), content, encoding=encoding)


def load(path, encoding="utf-8"):
    """Loads a file content"""
    with open(path, encoding=encoding, newline="") as handle:
        tmp = handle.read()
    return tmp


def mkdir(path):
    """Recursive mkdir, doesnt fail if already existing"""
    if os.path.exists(path):
        return
    os.makedirs(path)


def human_size(size_bytes):
    """
    format a size in bytes into a 'human' file size, e.g. B, KB, MB, GB, TB, PB
    Note that bytes will be reported in whole numbers but KB and above will have
    greater precision.  e.g. 43 B, 443 KB, 4.3 MB, 4.43 GB, etc
    """
    unit_size = 1000.0
    suffixes_table = [('B', 0), ('KB', 1), ('MB', 1), ('GB', 2), ('TB', 2), ('PB', 2)]

    num = float(size_bytes)
    the_precision = None
    the_suffix = None
    for suffix, precision in suffixes_table:
        the_precision = precision
        the_suffix = suffix
        if num < unit_size:
            break
        num /= unit_size

    if the_precision == 0:
        formatted_size = "%d" % num
    else:
        formatted_size = str(round(num, ndigits=the_precision))

    return f"{formatted_size}{the_suffix}"


def is_subdirectory(child_path, parent_path):
    """
    Check if a child_path is a subdirectory of parent_path.
    """
    child_path = Path(child_path).resolve()
    parent_path = Path(parent_path).resolve()
    return parent_path in child_path.parents
