import os
import shlex
import subprocess
import tempfile

from tome.errors import TomeException
from tome.internal.utils.files import load


def check_output_runner(command: str, stderr=None) -> str:
    """Run a command and return the output as a string.
        In case of error, raise a TomeException with the stderr output.

    :param command: Command to run
    :param stderr: Where to redirect the stderr, could be None
    :return: The output of the command
    """
    # Used to run several utilities, like Pacman detect, AIX version, uname, SCM
    tmp_file = tempfile.NamedTemporaryFile(prefix="output", delete=False)
    command_args = shlex.split(command)
    # We don't want stderr to print warnings that will mess the pristine outputs
    stderr = stderr or subprocess.PIPE
    with open(tmp_file.name, "w") as f_out:
        try:
            process = subprocess.Popen(command_args, stdout=f_out, stderr=stderr, shell=False)
        except Exception as error:
            raise TomeException(f"Could not run command '{command}':\n{error}") from error
        stderr = process.communicate()[1].decode()

    if process.returncode:
        # Only in case of error, we print also the stderr to know what happened
        raise TomeException(f"Command '{command}' failed with errorcode '{process.returncode}'\n{stderr}")

    output = load(tmp_file.name)
    # using delete=False and then manually deleting because it causes some
    # permission issues in windows otherwise
    tmp_file.close()
    os.unlink(tmp_file.name)
    return output
