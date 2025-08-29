from tests.utils.tools import TestClient
from tests.utils.files import temp_file



def test_install_empty_argument():
    """Test that the uninstall command fails when no arguments are passed.
    A source argument is required always for uninstallation.
    """
    client = TestClient()
    client.run("uninstall", assert_error=True)
    assert "Error: No installation source provided." in client.out


def test_uninstall_with_command_name():
    client = TestClient()
    client.run(f"new namespace:mycommand")
    client.run("install .")
    client.run("uninstall namespace:mycommand", assert_error=True)
    assert "You are trying to uninstall a command 'namespace:mycommand'" in client.out


def test_uninstall_script_file():
    """
    Test that the uninstall command fails when a script file is provided instead of a directory.
    """
    client = TestClient()
    dummy_script = temp_file(suffix='.py', prefix='cmd_foobar')
    client.run(f"uninstall '{dummy_script}'", assert_error=True)
    assert "Error: The following path does not exist or is not a directory: " in client.out