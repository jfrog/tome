import os
import sys
import textwrap

from tests.utils.tools import TestClient
from tome.internal.utils.files import mkdir


def test_run_unexistent_command():
    client = TestClient()
    client.run("notexistent", assert_error=True)
    assert "'notexistent' is not a tome command. See 'tome --help'." in client.out


def test_not_run_shell_when_help():
    client = TestClient()
    script_type = "sh"
    if sys.platform == "win32":
        script_type = "bat"
    client.run(f"new greetings:hello --type={script_type}")
    client.run("install .")
    client.run("greetings:hello --help")
    # The shell scripts were being executed by just calling to tome command --help
    assert "Hello, world!" not in client.out
    assert "Description of the command." in client.out


def test_run_shell_with_args():
    client = TestClient()
    mkdir(os.path.join(client.current_folder, "greetings"))
    script_sh = textwrap.dedent(
        '''
        #!/bin/bash
        echo "First arg: $1"
        echo "Second arg: $2"
        '''
    )
    script_bat = textwrap.dedent(
        '''
        @echo off
        echo First arg: %1
        echo Second arg: %2
        '''
    )
    if sys.platform == "win32":
        script_name = "tome_echo.bat"
        client.save({os.path.join(client.current_folder, "greetings", script_name): script_bat})
    else:
        script_name = "tome_echo.sh"
        client.save({os.path.join(client.current_folder, "greetings", script_name): script_sh})

    client.run("install .")
    client.run("greetings:echo value1 value2")
    assert "First arg: value1" in str(client.stdout)
    assert "Second arg: value2" in str(client.stdout)
