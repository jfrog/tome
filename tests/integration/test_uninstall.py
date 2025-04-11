import os
import textwrap

from tests.utils.tools import TestClient


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
