import os
import shutil
import sys
import textwrap

import pytest
import responses
from tome.internal.utils.files import mkdir, save
from tome.internal.utils.files import rmdir

from tests.utils.tools import TestClient
from tests.utils.tools import zipdir
from tests.utils.files import temp_folder


def _create_zip(folder, zippath=None):
    zippath = zippath or os.path.join(folder, "scripts.zip")
    zipdir(folder, zippath)
    return zippath


@responses.activate
def test_install_from_remote_zip():
    client = TestClient()
    fake_url = "http://fakeurl.com/scripts.zip"

    client.run("new mynamespace:mycommand")
    zip_path = _create_zip(client.current_folder)

    with open(zip_path, 'rb') as zip_content:
        responses.add(responses.GET, fake_url, body=zip_content.read(), status=200)

    client.run(f"install {fake_url}")
    client.run("list")
    assert "mynamespace:mycommand" in client.out

    client.run(f"uninstall {fake_url}")
    client.run("list")
    assert "mynamespace:mycommand" not in client.out


@responses.activate
@pytest.mark.parametrize("folder", ["subfolder", None])
def test_install_from_zip(folder):
    client = TestClient()
    fake_url = "http://fakeurl.com/scripts.zip"

    if folder:
        project_folder = os.path.join(client.current_folder, folder)
        mkdir(project_folder)
        with client.chdir(project_folder):
            client.run("new mynamespace:mycommand")
    else:
        client.run("new mynamespace:mycommand")

    zip_path = _create_zip(client.current_folder)

    with open(zip_path, 'rb') as zip_content:
        responses.add(responses.GET, fake_url, body=zip_content.read(), status=200)

    # from url
    folder_arg = f"--folder={folder}" if folder else ""
    client.run(f"install {fake_url} {folder_arg}")
    client.run("list")
    assert "mynamespace:mycommand" in client.out

    client.run(f"uninstall {fake_url}")
    client.run("list")
    assert "mynamespace:mycommand" not in client.out

    # local
    folder_arg = f"--folder={folder}" if folder else ""
    client.run(f"install '{os.path.join(client.current_folder, zip_path)}' {folder_arg}")
    client.run("list")
    assert "mynamespace:mycommand" in client.out

    client.run(f"uninstall '{os.path.join(client.current_folder, zip_path)}'")
    client.run("list")
    assert "mynamespace:mycommand" not in client.out


def test_install_folder_incompatible():
    client = TestClient()
    client.run("install . --folder=somefolder", assert_error=True)
    assert "--folder argument is only compatible" in client.out
    client.run("install . -e --folder=somefolder", assert_error=True)
    assert "--folder argument is only compatible" in client.out


@responses.activate
def test_install_from_remote_zip_invalid_folder():
    client = TestClient()
    fake_url = "http://fakeurl.com/scripts.zip"

    client.run("new mynamespace:mycommand")
    zip_path = _create_zip(client.current_folder)

    with open(zip_path, 'rb') as zip_content:
        responses.add(responses.GET, fake_url, body=zip_content.read(), status=200)

    folder_arg = "--folder=nonexistent"
    client.run(f"install {fake_url} {folder_arg}", assert_error=True)
    assert "not found in the archive" in client.out


def test_install_git_nonexistent():
    client = TestClient()
    git_repo_folder = os.path.join(client.current_folder, "git_repo")

    with client.chdir(git_repo_folder):
        client.run("new mynamespace:mycommand")

    commit = client.init_git_repo(folder=git_repo_folder)

    client.run(
        f"install '{os.path.join(client.current_folder, git_repo_folder)}/.git@{commit}' --folder=nonexistent",
        assert_error=True,
    )
    assert "Folder specified with --folder: 'nonexistent' does not exist" in client.out


@pytest.mark.parametrize("folder", [None, "examples"])
def test_install_from_git(folder):
    client = TestClient()
    git_repo_folder = os.path.join(client.current_folder, "git_repo")
    source_folder = os.path.join(git_repo_folder, folder) if folder else git_repo_folder

    mkdir(source_folder)
    with client.chdir(source_folder):
        client.run("new mynamespace:mycommand")

    folder_arg = f"--folder={folder}" if folder else ""

    commit = client.init_git_repo(folder=git_repo_folder)
    client.run(f"install '{source_folder}'")
    assert "Installed source:" in client.stdout
    client.run("list")
    assert "mynamespace:mycommand" in client.out

    client.run(f"uninstall '{source_folder}'")
    assert "Uninstalled source:" in client.stdout
    client.run("list")
    assert "mynamespace:mycommand" not in client.out

    client.run(f"install '{os.path.join(client.current_folder, git_repo_folder)}/.git@{commit}' {folder_arg}")
    client.run("list")
    assert "mynamespace:mycommand" in client.out

    client.run(f"uninstall '{os.path.join(client.current_folder, git_repo_folder)}/.git@{commit}'")
    client.run("list")
    assert "mynamespace:mycommand" not in client.out

    rmdir(os.path.join(client.cache_folder, "scripts"))
    client.run(f"install '{os.path.join(client.current_folder, git_repo_folder)}/.git@main' {folder_arg}")
    client.run("list")
    assert "mynamespace:mycommand" in client.out

    client.run(f"uninstall '{os.path.join(client.current_folder, git_repo_folder)}/.git@main'")
    client.run("list")
    assert "mynamespace:mycommand" not in client.out


def test_install_editable():
    client = TestClient()
    client.run("new mynamespace:mycommand")
    client.run("install . -e")
    client.run("list")
    assert "mynamespace:mycommand" in client.out

    client.run("uninstall .")
    client.run("list")
    assert "mynamespace:mycommand" not in client.out

    client.run("install -e", assert_error=True)
    assert "Error: No installation source provided." in client.out


@pytest.mark.parametrize("name", ["cmd", "sys", "mycmd", "os", "fnmatch", "platform", "requests", "rich"])
def test_install_cmd(name):
    # This was failing if the command is called any Python builtin or library import
    # The dynamic import machinery needs to load files by location
    c = TestClient()
    c.run(f"new mysp:{name}")
    c.run("install .")
    c.run("list")
    assert f"mysp:{name}" in c.out
    c.run(f"mysp:{name} myarg")
    assert "Tome command called with positional argument: myarg" in c.out


def test_install_git_editable():
    client = TestClient()
    git_repo_folder = "git_repo"

    mkdir(os.path.join(client.current_folder, git_repo_folder))

    client.run("new mynamespace:mycommand")

    shutil.move(
        os.path.join(client.current_folder, "mynamespace"), os.path.join(client.current_folder, git_repo_folder)
    )

    client.init_git_repo(folder=git_repo_folder)

    client.run(f"install '{os.path.join(client.current_folder, git_repo_folder)}' -e")
    client.run("list")
    assert "mynamespace:mycommand" in client.out


def test_install_empty_argument():
    """Test that the install command fails when no arguments are passed.
    A source argument is required always for installation.
    """
    client = TestClient()
    client.run("install", assert_error=True)
    assert "Error: No installation source provided." in client.out


def test_multiple_commands_one_file():
    client = TestClient()
    mkdir(os.path.join(client.current_folder, "greetings"))
    tome_script = textwrap.dedent(
        '''
        from tome.command import tome_command

        @tome_command()
        def hello(tome_api, parser, *args):
            """hello tome."""
            parser.add_argument('message', help="hello message")
            args = parser.parse_args(*args)
            print(f"hello: {args.message}")


        @tome_command()
        def bye(tome_api, parser, *args):
            """bye tome."""
            parser.add_argument('message', help="bye message")
            args = parser.parse_args(*args)
            print(f"bye: {args.message}")
    '''
    )
    client.save({os.path.join(client.current_folder, "greetings", "greetings-commands.py"): tome_script})
    client.run("install .")
    client.run("list")
    assert "greetings:bye" in client.out
    assert "greetings:hello" in client.out
    client.run("greetings:hello 'whatever'")
    assert "hello: whatever" in client.out
    client.run("greetings:bye 'whatever'")
    assert "bye: whatever" in client.out


def test_multiple_commands_and_subcommands():
    client = TestClient()
    mkdir(os.path.join(client.current_folder, "greetings"))
    tome_script = textwrap.dedent(
        '''
        from tome.command import tome_command

        @tome_command()
        def hello(tome_api, parser, *args):
            """hello tome."""

        @tome_command(parent=hello)
        def hola(tome_api, parser, *args):
            """hello tome in spanish."""
            parser.add_argument('message', help="hello message in spanish")
            args = parser.parse_args(*args)
            print(f"hello: {args.message}")

        @tome_command(parent=hello)
        def ciao(tome_api, parser, *args):
            """hello tome in italian."""
            parser.add_argument('message', help="hello message in italian")
            args = parser.parse_args(*args)
            print(f"hello: {args.message}")

        @tome_command()
        def bye(tome_api, parser, *args):
            """bye tome."""

        @tome_command(parent=bye)
        def adios(tome_api, parser, *args):
            """bye tome in spanish."""
            parser.add_argument('message', help="bye message in spanish")
            args = parser.parse_args(*args)
            print(f"bye: {args.message}")

        @tome_command(parent=bye)
        def addio(tome_api, parser, *args):
            """bye tome in italian."""
            parser.add_argument('message', help="bye message in italian")
            args = parser.parse_args(*args)
            print(f"bye: {args.message}")
    '''
    )
    client.save({os.path.join(client.current_folder, "greetings", "greetings-commands.py"): tome_script})
    client.run("install .")
    client.run("list")
    assert "greetings:hello" in client.out
    assert "greetings:bye" in client.out
    client.run("greetings:hello --help")
    assert "{hola,ciao}" in client.out
    client.run("greetings:bye --help")
    assert "{adios,addio}" in client.out


def test_commands_from_script():
    client = TestClient()
    mkdir(os.path.join(client.current_folder, "greetings"))
    script = textwrap.dedent(
        '''
        echo "hello world"
        '''
    )

    client.save({os.path.join(client.current_folder, "greetings", "tome_echo.sh"): script})
    client.save({os.path.join(client.current_folder, "greetings", "tome_echo.bat"): script})

    client.run("install .")
    client.run("list")

    assert "greetings:echo-bat" in client.out
    assert "greetings:echo-sh" in client.out

    command_name = "greetings:echo-bat" if sys.platform == "win32" else "greetings:echo-sh"

    client.run(f"{command_name} --help")

    assert "Command to run the script: " in client.out

    script_name = "tome_echo.bat" if sys.platform == "win32" else "tome_echo.sh"
    assert script_name in client.out


def test_commands_script_and_tomescript():
    client = TestClient()
    mkdir(os.path.join(client.current_folder, "greetings"))
    script = textwrap.dedent(
        '''
        echo "hello world"
        '''
    )
    client.save({os.path.join(client.current_folder, "greetings", "tome_echo.sh"): script})
    tome_script = textwrap.dedent(
        '''
        from tome.command import tome_command

        @tome_command()
        def hello(tome_api, parser, *args):
            """hello tome."""

        @tome_command(parent=hello)
        def hola(tome_api, parser, *args):
            """hello tome in spanish."""
            parser.add_argument('message', help="hello message in spanish")
            args = parser.parse_args(*args)
            print(f"hello: {args.message}")

        @tome_command(parent=hello)
        def ciao(tome_api, parser, *args):
            """hello tome in italian."""
            parser.add_argument('message', help="hello message in italian")
            args = parser.parse_args(*args)
            print(f"hello: {args.message}")

        @tome_command()
        def bye(tome_api, parser, *args):
            """bye tome."""

        @tome_command(parent=bye)
        def adios(tome_api, parser, *args):
            """bye tome in spanish."""
            parser.add_argument('message', help="bye message in spanish")
            args = parser.parse_args(*args)
            print(f"bye: {args.message}")

        @tome_command(parent=bye)
        def addio(tome_api, parser, *args):
            """bye tome in italian."""
            parser.add_argument('message', help="bye message in italian")
            args = parser.parse_args(*args)
            print(f"bye: {args.message}")
    '''
    )
    client.save({os.path.join(client.current_folder, "greetings", "greetings-commands.py"): tome_script})
    client.run("install .")
    client.run("list")
    assert "greetings:echo" in client.out
    assert "greetings:hello" in client.out
    assert "greetings:bye" in client.out
    client.run("greetings:hello --help")
    assert "{hola,ciao}" in client.out
    client.run("greetings:bye --help")
    assert "{adios,addio}" in client.out


def test_tomeignore_file():
    tc = TestClient()
    source = temp_folder()
    mkdir(os.path.join(source, "greetings"))
    mkdir(os.path.join(source, "greetings", "subgreetings"))
    mkdir(os.path.join(source, "tests"))
    mkdir(os.path.join(source, "utils"))
    mkdir(os.path.join(source, "assets"))
    mkdir(os.path.join(source, "pepetests"))
    save(
        os.path.join(source, ".tomeignore"),
        textwrap.dedent("""
    tests/*
    utils
    subgreetings #  This is a comment which should be ignored
    # assets
    """),
    )
    # TODO:     greetings/subgreetings does not filter out subgreetings-commands.py,
    #  you have to only use the last folder, which is not ideal
    # adding fake command to not raise error for not having any tome commands
    save(os.path.join(source, "greetings", "greetings-commands.py"), "@tome_command()")
    save(os.path.join(source, "greetings", "subgreetings", "subgreetings-commands.py"), "@tome_command()")
    save(os.path.join(source, "assets", "image.png"), "")
    save(os.path.join(source, "pepetests", "test_pepe.py"), "")

    test_file_path = os.path.join(source, "tests", "test_greetings.py")
    save(test_file_path, "")

    save(os.path.join(source, "utils", "files.py"), "")

    tc.run(f'install "{source}" -v')
    assert "test_greetings.py" not in tc.out
    assert "files.py" not in tc.out
    assert "subgreetings-commands.py" not in tc.out
    assert "image.png" in tc.out
    assert "test_pepe.py" in tc.out


def test_validate_folder_install():
    client = TestClient()
    client.run("new mynamespace:mycommand")
    client.run("install mynamespace", assert_error=True)
    assert "No valid tome commands were found" in client.out

    client.run("install mynamespace -e", assert_error=True)
    assert "No valid tome commands were found" in client.out


def test_validate_git_install():
    client = TestClient()
    git_repo_folder = os.path.join(client.current_folder, "git_repo")

    # Create an invalid structure in the git repository: place the command in a nested subdirectory (more than one level deep)
    nested_folder = os.path.join(git_repo_folder, "subfolder", "nested")
    os.makedirs(nested_folder, exist_ok=True)
    with client.chdir(nested_folder):
        client.run("new mynamespace:mycommand")

    client.init_git_repo(folder=git_repo_folder)

    install_source = f"{os.path.join(client.current_folder, git_repo_folder)}/.git"
    client.run(f"install '{install_source}'", assert_error=True)
    assert "No valid tome commands were found in the cloned repository" in client.out
