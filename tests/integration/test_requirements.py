import json
import os
import textwrap

import responses

from tests.utils.tools import TestClient
from tests.utils.tools import zipdir


def test_install_local_with_requirements():
    c = TestClient()
    c.run("new mynamespace:mycommand")
    c.save({"requirements.txt": "pyyaml"})
    c.run("install . -e")
    assert "Requirement already satisfied: pyyaml" or ("Successfully installed" and "pyyaml") in c.out
    c.run("uninstall .")
    c.run("install .")
    assert "Requirement already satisfied: pyyaml" or ("Successfully installed" and "pyyaml") in c.out


def test_install_editable_with_requirements_fail():
    c = TestClient()
    c.run("new mynamespace:mycommand")
    c.save({"requirements.txt": "tomato_this_wont_exist"})
    c.run("install . -e -v", assert_error=True)
    # TODO: Decide if better to remove these commands, disable or what
    assert "ERROR: No matching distribution found for tomato_this_wont_exist" in c.out
    assert "Error: pip install failed. These commands might not work correctly" in c.out


@responses.activate
def test_remote():
    # TODO: Copied from test_install.py, factor out common
    c = TestClient()
    fake_url = "http://fakeurl.com/scripts.zip"
    c.run("new mynamespace:mycommand")
    c.save({"requirements.txt": "pyyaml"})
    zippath = os.path.join(c.current_folder, "scripts.zip")
    zipdir(c.current_folder, zippath)

    with open(zippath, 'rb') as zip_content:
        responses.add(responses.GET, fake_url, body=zip_content.read(), status=200)

    c.run(f"install {fake_url} -v")
    assert "Requirement already satisfied: pyyaml" in c.out
    c.run("list *")
    assert "mynamespace:mycommand" in str(c.out)

    # sources update to a non existing package, now it will fail
    c.save({"requirements.txt": "tomato_this_wont_exist"})
    zipdir(c.current_folder, zippath)
    with open(zippath, 'rb') as zip_content:  # TODO: It is weird that this has to be repeated
        responses.add(responses.GET, fake_url, body=zip_content.read(), status=200)

    c.run(f"install {fake_url} -v", assert_error=True)
    assert "ERROR: No matching distribution found for tomato_this_wont_exist" in c.out
    assert "Error: pip install failed. These commands might not work correctly" in c.out


def setup_package(client, package_name):
    init_file = "def hello():\n    print(\"I'm a tomato!\")\n"
    setup_py = textwrap.dedent(f"""
            from setuptools import setup, find_packages
            setup(
                name="{package_name}",
                version="0.1",
                packages=find_packages(),
                install_requires=[],
            )
            """)
    client.save(
        {
            os.path.join(client.current_folder, package_name, 'setup.py'): setup_py,
            os.path.join(client.current_folder, package_name, package_name, '__init__.py'): init_file,
        }
    )


def test_install_create_venv():
    client = TestClient()
    setup_package(client, "tomato")
    commands_folder = os.path.join(client.current_folder, "tome_commands")

    greet = textwrap.dedent('''
        from tome.command import tome_command
        @tome_command()
        def mycommand(tome_api, parser, *args):
            """Placeholder for a new tome script."""
            import tomato
            tomato.hello()
    ''')
    client.save({os.path.join(commands_folder, "hello", "greet.py"): greet})
    tomato_path = os.path.join(client.current_folder, "tomato")
    client.save({os.path.join(commands_folder, "requirements.txt"): f"{tomato_path}\n"})
    client.run_command("pip list")
    assert "tomato" not in client.out
    client.run("install tome_commands --create-env")
    assert "Created the virtual environment located at" in client.out
    client.run("list")
    assert "hello:mycommand      Placeholder for a new tome script" in client.out
    client.run("hello:mycommand", assert_error=True)
    # this errors unless we activate the venv we have just created
    assert "No module named 'tomato'" in client.out
    client.run("info hello:mycommand --format=json")
    tome_info = json.loads(client.out)
    env_path = tome_info.get("env_path")
    assert env_path, "Expected to find the env path in the output"
    client.run_command("pip list")
    assert "tomato" not in client.out


def test_install_create_venv_editable():
    # TODO: This is repeated from above, refactor
    client = TestClient()
    setup_package(client, "tomato")
    commands_folder = os.path.join(client.current_folder, "tome_commands")

    greet = textwrap.dedent('''
        from tome.command import tome_command
        @tome_command()
        def mycommand(tome_api, parser, *args):
            """Placeholder for a new tome script."""
            import tomato
            tomato.hello()
    ''')
    client.save({os.path.join(commands_folder, "hello", "greet.py"): greet})
    tomato_path = os.path.join(client.current_folder, "tomato")
    client.save({os.path.join(commands_folder, "requirements.txt"): f"{tomato_path}\n"})
    client.run_command("pip list")
    assert "tomato" not in client.out
    client.run("install -e tome_commands --create-env")
    assert "Created the virtual environment located at" in client.out
    client.run("list")
    assert "hello:mycommand (e)  Placeholder for a new tome script." in client.out
    client.run("hello:mycommand", assert_error=True)
    # this errors unless we activate the venv we have just created
    assert "No module named 'tomato'" in client.out
    client.run("info hello:mycommand --format=json")
    tome_info = json.loads(client.out)
    env_path = tome_info.get("env_path")
    assert env_path, "Expected to find the env path in the output"
    client.run_command("pip list")
    assert "tomato" not in client.out
