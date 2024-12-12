from tests.utils.tools import TestClient


def test_show_only_built_in_help():
    client = TestClient()
    # Editable command
    client.run("new mynamespace:mycommand")
    client.run("install . -e")
    # Show only built-in commands
    client.run("--help")
    assert all([command in client.out for command in ["install", "list", "uninstall", "new"]])
    assert "mynamespace:mycommand" not in client.out
