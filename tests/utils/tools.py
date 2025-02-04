import os
import shlex
import shutil
import socket
import sys
import threading
import time
import traceback
import zipfile
from contextlib import contextmanager
from unittest import mock

from tome.api.api import TomeAPI, get_tome_home
from tome.cli import Cli
from tome.errors import TomeException
from tome.exit_codes import ERROR_GENERAL
from tome.exit_codes import SUCCESS
from tome.internal.utils.files import load
from tome.internal.utils.files import mkdir
from tome.internal.utils.files import save
from tome.internal.utils.files import save_files

from tests.utils.files import temp_folder
from tests.utils.mocks import RedirectedInputStream
from tests.utils.mocks import RedirectedTestOutput
from tests.utils.scm import create_local_git_repo


@contextmanager
def redirect_output(stderr, stdout=None):
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    # redirecting both of them to the same target for the moment
    # to assign to Testclient out
    sys.stdout = stdout or stderr
    sys.stderr = stderr
    try:
        yield
    finally:
        sys.stdout = original_stdout
        sys.stderr = original_stderr


@contextmanager
def redirect_input(target):
    original_stdin = sys.stdin
    sys.stdin = target
    try:
        yield
    finally:
        sys.stdin = original_stdin


class TestClient:
    """Test wrap of the tome application to launch tests in the same way as
    in command line
    """

    __test__ = False  # Avoids pytest Collection warning

    def __init__(self, cache_folder=None, current_folder=None, inputs=None):
        """
        current_folder: Current execution folder
        logins is a list of (user, password) for auto input in order
        if required==> [("lasote", "mypass"), ("other", "otherpass")]
        """

        self.cache_folder = get_tome_home(cache_folder, temp_folder())

        self.current_folder = current_folder or temp_folder()

        # Once the client is ready, modify the configuration
        mkdir(self.current_folder)

        self.out = ""
        self.stdout = RedirectedTestOutput()
        self.stderr = RedirectedTestOutput()
        self.user_inputs = RedirectedInputStream([])
        self.inputs = inputs or []

    def load(self, filename):
        return load(os.path.join(self.current_folder, filename))

    @contextmanager
    def chdir(self, newdir):
        old_dir = self.current_folder
        if not os.path.isabs(newdir):
            newdir = os.path.join(old_dir, newdir)
        mkdir(newdir)
        self.current_folder = newdir
        try:
            yield
        finally:
            self.current_folder = old_dir

    @contextmanager
    def mocked_io(self):
        def mock_get_pass(*args, **kwargs):
            return self.user_inputs.readline()

        with redirect_output(self.stderr, self.stdout):
            with redirect_input(self.user_inputs):
                with mock.patch("getpass.getpass", mock_get_pass):
                    yield

    def _run_cli(self, command_line, assert_error=False):
        current_dir = os.getcwd()
        os.chdir(self.current_folder)
        old_path = sys.path[:]
        old_modules = list(sys.modules.keys())

        args = shlex.split(command_line)

        try:
            self.api = TomeAPI(cache_folder=self.cache_folder)
            command = Cli(self.api)
        except TomeException as e:
            sys.stderr.write(f"Error in tome initialization: {e}")
            return ERROR_GENERAL

        error = SUCCESS
        trace = None
        try:
            command.run(args)
        except BaseException as e:  # Capture all exceptions as argparse
            trace = traceback.format_exc()
            error = command.exception_exit_error(e)
        finally:
            sys.path = old_path
            os.chdir(current_dir)
            # Reset sys.modules to its prev state. A .copy() DOES NOT WORK
            added_modules = set(sys.modules).difference(old_modules)
            for added in added_modules:
                sys.modules.pop(added, None)
        self._handle_cli_result(command_line, assert_error=assert_error, error=error, trace=trace)
        return error

    def run(self, command_line, assert_error=False, redirect_stdout=None, redirect_stderr=None, inputs=None):
        """run a single command as in the command line.
        If user or password is filled, user_io will be mocked to return this
        tuple if required
        """
        from tests.utils.mocks import RedirectedTestOutput

        self.user_inputs = RedirectedInputStream(inputs or self.inputs)
        self.stdout = RedirectedTestOutput()  # Initialize each command
        self.stderr = RedirectedTestOutput()
        self.out = ""
        with self.mocked_io():
            try:
                return self._run_cli(command_line, assert_error=assert_error)
            finally:
                self.stdout = str(self.stdout)
                self.stderr = str(self.stderr)
                self.out = self.stderr + self.stdout
                if redirect_stdout:
                    save(os.path.join(self.current_folder, redirect_stdout), self.stdout)
                if redirect_stderr:
                    save(os.path.join(self.current_folder, redirect_stderr), self.stderr)

    def run_command(self, command, cwd=None, assert_error=False):
        from tests.utils.mocks import RedirectedTestOutput

        self.stdout = RedirectedTestOutput()  # Initialize each command
        self.stderr = RedirectedTestOutput()
        try:
            with redirect_output(self.stderr, self.stdout):
                from tome.internal.utils.runners import tome_run

                ret = tome_run(command, cwd=cwd or self.current_folder)
        finally:
            self.stdout = str(self.stdout)
            self.stderr = str(self.stderr)
            self.out = self.stderr + self.stdout
        self._handle_cli_result(command, assert_error=assert_error, error=ret)
        return ret

    def _handle_cli_result(self, command, assert_error, error, trace=None):
        if (assert_error and not error) or (not assert_error and error):
            if assert_error:
                msg = " Command succeeded (failure expected): "
            else:
                msg = " Command failed (unexpectedly): "
            exc_message = "\n{header}\n{cmd}\n{output_header}\n{output}\n".format(
                header=f'{msg:=^80}',
                output_header='{:=^80}'.format(" Output: "),
                cmd=command,
                output=str(self.stderr) + str(self.stdout) + "\n" + str(self.out),
            )
            if trace:
                exc_message += '{:=^80}'.format(" Traceback: ") + f"\n{trace}"
            raise Exception(exc_message)

    def save(self, files, path=None, clean_first=False):
        """
        helper metod, will store files in the current folder
        param files: dict{filename: filecontents}
        """
        path = path or self.current_folder
        if clean_first:
            shutil.rmtree(self.current_folder, ignore_errors=True)
        files = {f: str(content) for f, content in files.items()}
        save_files(path, files)
        if not files:
            mkdir(self.current_folder)

    def init_git_repo(self, files=None, branch=None, submodules=None, folder=None, origin_url=None, main_branch="main"):
        if folder is not None:
            folder = os.path.join(self.current_folder, folder)
        else:
            folder = self.current_folder
        _, commit = create_local_git_repo(
            files, branch, submodules, folder=folder, origin_url=origin_url, main_branch=main_branch
        )
        return commit


def get_free_port():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))
    ret = sock.getsockname()[1]
    sock.close()
    return ret


def zipdir(path, zipfilename):
    with zipfile.ZipFile(zipfilename, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(path):
            for f in files:
                file_path = os.path.join(root, f)
                if file_path == zipfilename:
                    continue
                relpath = os.path.relpath(file_path, path)
                z.write(file_path, relpath)


@contextmanager
def environment_update(env_vars):
    old_env = dict(os.environ)
    sets = {k: v for k, v in env_vars.items() if v is not None}
    unsets = [k for k, v in env_vars.items() if v is None]
    os.environ.update(sets)
    for var in unsets:
        os.environ.pop(var, None)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_env)
