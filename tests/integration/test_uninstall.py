import os
import textwrap

from tests.utils.tools import TestClient


def test_both_source_requirements():
    """Only source or requirements can be passed, not both."""
    client = TestClient()
    client.run("uninstall source_folder -f tomefile.yaml", assert_error=True)
    assert "Error: Cannot specify both a source and a 'tomefile.yaml'." in client.out


def test_install_empty_argument():
    """Test that the uninstall command fails when no arguments are passed.
    A source argument is required always for uninstallation.
    """
    client = TestClient()
    client.run("uninstall", assert_error=True)
    assert "Error: No installation source provided." in client.out


def test_uninstall_requirements():
    """Test that the uninstall command works with a requirement argument."""
    client = TestClient()
    tomefile_yaml = textwrap.dedent(
        f'''
        sources:
        - origin: {os.path.join(client.current_folder, 'git_repo_folder')}
    '''
    )
    client.save({os.path.join(client.current_folder, "tomefile.yaml"): tomefile_yaml})
    client.run("uninstall -f tomefile.yaml")
    assert "" in client.out
