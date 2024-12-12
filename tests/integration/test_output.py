from tests.utils.tools import TestClient


def test_verbosity():
    client = TestClient()
    client.run("new mynamespace:mycommand -q")
    assert client.out == ""
    client.run("install . -q")
    assert client.out == ""
    client.run("uninstall . -q")
    assert client.out == ""

    client.run("install .")
    assert "Copied" in client.out
    client.run("uninstall .")
    assert "Uninstalled" in client.out

    # test verbosity with subcommands
    client.run("vault --help")
    assert "verbose" in client.out
    assert "quiet" in client.out

    client.run("vault create --help")
    assert "verbose" in client.out
    assert "quiet" in client.out

    client.run("vault create -p potato -q")
    assert "" == client.out
