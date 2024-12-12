import os
import tempfile
from io import StringIO

import pytest

import tests.utils.runners
from tome.errors import TomeException
from tome.internal.utils import runners


@pytest.mark.parametrize(
    "command, exp_code, exp_output",
    [
        ("python -c \"print('Hello, World!')\"", 0, "Hello, World!\n"),
        ("python -c \"import sys; sys.exit(1)\"", 1, ""),
    ],
)
def test_detect_runner(command, exp_code, exp_output):
    """The detect_runner should be able to run any command and return the output."""
    runner_code, runner_out = runners.detect_runner(command)
    assert runner_code == exp_code
    assert runner_out.strip() == exp_output.strip()


def test_detect_runner_failure():
    """The detect_runner should raise a TomeException when the command is not found."""
    with pytest.raises(TomeException) as exc_info:
        runners.detect_runner("the command does not exist")
    assert "Could not run command 'the command does not exist'" in str(exc_info.value)


def test_tome_run_only_command():
    """The tome_run should be able to run a command and preserve the output."""
    runner_code = runners.tome_run("python -c \"print('Rocinante')\"")
    assert runner_code == 0


def test_tome_run_stdout():
    stdout = StringIO()
    stderr = StringIO()
    runner_code = runners.tome_run("python -c \"print('Rocinante')\"", stdout=stdout, stderr=stderr)
    assert runner_code == 0
    assert "Rocinante" in stdout.getvalue()
    assert stderr.getvalue() == ""


def test_tome_run_stderr():
    stdout = StringIO()
    stderr = StringIO()
    runner_code = runners.tome_run(
        "python -c \"import sys; sys.stderr.write('Rocinante')\"", stdout=stdout, stderr=stderr
    )
    assert runner_code == 0
    assert stderr.getvalue() == "Rocinante"
    assert stdout.getvalue() == ""


def test_tome_run_cwd():
    stdout = StringIO()
    stderr = StringIO()
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file_path = os.path.join(temp_dir, "test.txt")
        with open(test_file_path, "w") as test_file:
            test_file.write("Sancho Panza")
        runner_code = runners.tome_run(
            f"python -c \"with open('test.txt', 'r') as f: print(f.read().strip())\"",
            cwd=temp_dir,
            stdout=stdout,
            stderr=stderr,
        )
        assert runner_code == 0
        assert stdout.getvalue().strip() == "Sancho Panza"
        assert stderr.getvalue() == ""


def test_tome_run_failure():
    stdout = StringIO()
    stderr = StringIO()
    with pytest.raises(TomeException) as exc_info:
        runners.tome_run("command-that-does-not-exist", stdout=stdout, stderr=stderr)
    assert "Could not run command" in str(exc_info.value)
