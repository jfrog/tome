import json
import os
import textwrap

import pytest

from tome.internal.cache import TomePaths
from tome.internal.utils.files import mkdir, rmdir

from tests.utils.tools import TestClient


@pytest.fixture
def client():
    client = TestClient()

    mkdir(os.path.join(client.current_folder, "greetings"))
    mkdir(os.path.join(client.current_folder, "deployments"))

    tome_script = textwrap.dedent("""
    from tome.command import tome_command

    @tome_command()
    def hello(tome_api, parser, *args):
        '''Saying hello tome.'''
        parser.add_argument('message', help="Show hello message")
        args = parser.parse_args(*args)
        print(f"hello: {args.message}")


    @tome_command()
    def bye(tome_api, parser, *args):
        '''Saying bye tome.'''
        parser.add_argument('message', help="Show bye message")
        args = parser.parse_args(*args)
        print(f"bye: {args.message}")
    """)
    client.save({os.path.join(client.current_folder, "greetings", "greetings-commands.py"): tome_script})

    tome_script = textwrap.dedent("""
    from tome.command import tome_command

    @tome_command()
    def deploy(tome_api, parser, *args):
        '''Enable a deployment.'''
        parser.add_argument('message', help="Call deploy function")
        args = parser.parse_args(*args)
        print(f"Deploy: {args.message}")


    @tome_command()
    def release(tome_api, parser, *args):
        '''Public a new release.'''
        parser.add_argument('message', help="Deploy a release")
        args = parser.parse_args(*args)
        print(f"Release: {args.message}")
    """)
    client.save({os.path.join("deployments", "deployments-commands.py"): tome_script})
    client.run("install .")

    rmdir(os.path.join(client.current_folder, "greetings"))
    rmdir(os.path.join(client.current_folder, "deployments"))

    # Editable commands
    client.run("new mynamespace:mycommand")
    client.run("install . -e")

    return client


@pytest.mark.parametrize(
    "pattern, expected, not_expected",
    [
        # empty pattern
        (
            "",
            ["deployments:deploy", "greetings:bye"],
            ["Install scripts from various sources."],  # built-in does not appear
        ),
        # pattern for docs
        (
            "say",
            ["greetings:bye", "greetings:hello"],
            ["deployments:deploy   Enable a deployment."],
        ),
        # pattern for commands
        (
            "mycommand",
            ["mynamespace:mycommand"],
            ["greetings:bye"],
        ),
    ],
)
def test_list(pattern, expected, not_expected, client):
    client.run(f"list '{pattern}'")
    for line in expected:
        assert line in client.out
    for line in not_expected:
        assert line not in client.out


def test_empty_pattern():
    """
    This command should not show any matches because we're filtering the built-in commands
    """
    client = TestClient()
    client.run("list")
    assert "Error: No matches were found for '*' pattern." in client.out


def test_list_failed_imported():
    client = TestClient()
    os.mkdir(os.path.join(client.current_folder, "hello"))
    greet = textwrap.dedent(f'''
        import os
        from tome.command import tome_command
        {{normal_import}}
        @tome_command()
        def mycommand(tome_api, parser, *args):
            """Placeholder for a new tome script."""
            {{lazy_import}}
            pass
    ''')
    client.save(
        {os.path.join("hello", "greet.py"): greet.format(normal_import="import unknown_import", lazy_import="")}
    )
    client.run("install .")
    client.run("list")
    assert "Error: Error loading command 'greet.py' from" in client.out
    # the command listing will fail, we need to make the import lazy if we want to fix this
    assert "Loading command failed: No module named" in client.out
    # if we try to run the command we get a message about the failed loading
    client.run("hello:mycommand", assert_error=True)
    assert "There was an error when installing the 'hello:mycommand' command" in client.out
    # import lazy, we dont have errors
    client.run("uninstall .")
    client.save(
        {os.path.join("hello", "greet.py"): greet.format(normal_import="", lazy_import="import unknown_import")}
    )
    client.run("install .")
    client.run("list")
    # we import lazy, no errors listing
    assert "Error: Error loading command 'greet.py' from" not in client.out
    assert "hello:mycommand      Placeholder for a new tome script." in client.out
    # but errors show when running the command
    client.run("hello:mycommand", assert_error=True)
    assert "No module named 'unknown_import'" in client.out


def test_formats_json():
    client = TestClient()
    client.run("new mynamespace:mycommand")
    client.run("install .")
    client.run("list --format json")

    origin_key = os.path.abspath(client.current_folder)
    namespace_key = "mynamespace"
    command_key = "mycommand"

    expected_output = {
        origin_key: {
            namespace_key: {command_key: {"doc": "Description of the command.", "type": "cache", "error": None}}
        }
    }

    assert json.loads(client.out) == expected_output


def test_grouped_output():
    client = TestClient()
    client.run(f"new space_l:my-l")
    client.run("install .")

    rmdir(os.path.join(client.current_folder, "space1"))

    client.run(f"new space_e:mycommand-e")
    client.run("install . -e")

    git_repo_folder = os.path.join(client.current_folder, "git_repo")
    with client.chdir(git_repo_folder):
        client.run("new space_g:mycommand-git")

    client.init_git_repo(folder=git_repo_folder)

    install_source = f"{os.path.join(client.current_folder, git_repo_folder)}/.git"
    client.run(f"install '{install_source}'")

    client.run("list")
    print(client.out)
