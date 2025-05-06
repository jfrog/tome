import os
import platform
import shutil
import textwrap

from tests.integration.test_requirements import setup_package
from tests.utils.tools import TestClient
from tome.internal.utils.files import mkdir


def test_info():
    client = TestClient()

    mkdir(os.path.join(client.current_folder, "tome_commands"))

    client.run("new mynamespace:mycommand")
    client.run("new mynamespace:mycommand2")
    shutil.move(
        os.path.join(client.current_folder, "mynamespace"),
        os.path.join(client.current_folder, "tome_commands", "mynamespace"),
    )

    client.run("install tome_commands")
    client.run("info mynamespace:mycommand")
    assert "name: mycommand" in client.stdout
    assert "namespace: mynamespace" in client.stdout
    assert "type: cache" in client.stdout
    client.run("info mynamespace:mycommand2")
    assert "name: mycommand2" in client.stdout
    assert "namespace: mynamespace" in client.stdout
    assert "type: cache" in client.stdout
    client.run("uninstall tome_commands")

    # try with editables
    client.run("install tome_commands -e")
    client.run("info mynamespace:mycommand")
    assert "name: mycommand" in client.stdout
    assert "namespace: mynamespace" in client.stdout
    assert "type: editable" in client.stdout
    client.run("info mynamespace:mycommand2")
    assert "name: mycommand2" in client.stdout
    assert "namespace: mynamespace" in client.stdout
    assert "type: editable" in client.stdout
    client.run("uninstall tome_commands")

    # let's try with a command with requirements
    setup_package(client, "tomato")
    tomato_path = os.path.join(client.current_folder, "tomato")
    client.save({os.path.join("tome_commands", "requirements.txt"): f"{tomato_path}\n"})
    client.run("install tome_commands --create-env")
    client.run("info mynamespace:mycommand")
    assert "name: mycommand" in client.stdout
    assert "namespace: mynamespace" in client.stdout
    assert "type: cache" in client.stdout
    client.run("info mynamespace:mycommand2")
    assert "name: mycommand2" in client.stdout
    assert "namespace: mynamespace" in client.stdout
    assert "type: cache" in client.stdout
    assert "env_path:" in client.stdout
    client.run("uninstall tome_commands")


def test_info_shell_commands():
    c = TestClient()
    script = textwrap.dedent("""\
        echo "hello world"
        """)
    script_name = "tome_echo.sh" if platform.system() != "Windows" else "tome_echo.bat"
    command_name = "greetings:echo-sh" if platform.system() != "Windows" else "greetings:echo-bat"
    c.save({os.path.join(c.current_folder, "greetings", script_name): script})
    c.run("install .")
    c.run(f"info {command_name}")
    # TODO: Check more things: runner, script
    print(c.out)
    assert "name: echo" in c.out
