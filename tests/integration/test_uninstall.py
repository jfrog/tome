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
