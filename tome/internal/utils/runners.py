import os
import shlex
import subprocess
import sys
from contextlib import contextmanager
from io import StringIO

from rich.live import Live
from rich.spinner import Spinner

from tome.api.output import TomeOutput
from tome.errors import TomeException

if getattr(sys, 'frozen', False) and 'LD_LIBRARY_PATH' in os.environ:
    # http://pyinstaller.readthedocs.io/en/stable/runtime-information.html#ld-library-path-libpath-considerations
    pyinstaller_bundle_dir = (
        os.environ['LD_LIBRARY_PATH'].replace(os.environ.get('LD_LIBRARY_PATH_ORIG', ''), '').strip(';:')
    )

    @contextmanager
    def pyinstaller_bundle_env_cleaned():
        """Removes the pyinstaller bundle directory from LD_LIBRARY_PATH"""
        ld_library_path = os.environ['LD_LIBRARY_PATH']
        os.environ['LD_LIBRARY_PATH'] = ld_library_path.replace(pyinstaller_bundle_dir, '').strip(';:')
        yield
        os.environ['LD_LIBRARY_PATH'] = ld_library_path

else:

    @contextmanager
    def pyinstaller_bundle_env_cleaned():
        yield


def detect_runner(command: str) -> (int, str):
    """Run a command and return the return code and the output as a string.
    :param command: Command to run
    :return: The return code and the output of the command
    """
    command_list = shlex.split(command)
    try:
        proc = subprocess.Popen(
            command_list,
            bufsize=1,
            universal_newlines=True,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = proc.communicate()
        return proc.returncode, stdout + stderr
    except Exception as error:
        raise TomeException(f"Could not run command '{command}':\n{error}") from error


def tome_run(command, stdout=None, stderr=None, cwd=None):
    """Run a command and print the output to stdout and stderr.
    @param stderr: Instead of print to sys.stderr print to that stream. Could be None
    @param command: Command to execute
    @param stdout: Instead of print to sys.stdout print to that stream. Could be None
    @param cwd: Move to directory to execute
    """
    # If we are not at least in -v mode, we should not print the output of the command
    stdout = stdout or (StringIO() if not TomeOutput.is_verbose() else sys.stderr)
    stderr = stderr or (StringIO() if not TomeOutput.is_verbose() else sys.stderr)

    out = subprocess.PIPE if isinstance(stdout, StringIO) else stdout
    err = subprocess.PIPE if isinstance(stderr, StringIO) else stderr

    with pyinstaller_bundle_env_cleaned():
        try:
            command_list = shlex.split(command)
            proc = subprocess.Popen(command_list, shell=False, stdout=out, stderr=err, cwd=cwd)
        except Exception as error:
            raise TomeException(f"Could not run command '{command}':\n{error}") from error

        proc_stdout, proc_stderr = proc.communicate()
        # If the output is piped, like user provided a StringIO or testing, the communicate
        # will capture and return something when thing finished
        if proc_stdout:
            stdout.write(proc_stdout.decode("utf-8", errors="ignore"))
        if proc_stderr:
            stderr.write(proc_stderr.decode("utf-8", errors="ignore"))
        return proc.returncode
