import os

from tests.utils.tools import TestClient
from tome.internal.utils.files import rmdir


def test_simple():
    client = TestClient()
    client.run("new misc:hello-world")
    client.run("install .")
    client.run("test misc:hello-world")
    assert "1 passed" in client.out


def test_multiple():
    client = TestClient()
    client.run("new greetings:hello-world")
    client.run("new greetings:bye-world")
    client.run("install .")
    client.run("test greetings:*")
    assert "2 passed" in client.out


def test_mixed():
    client = TestClient()
    client.run("new greetings:hello-world")
    client.run("new greetings:bye-world")
    client.run("new misc:other-command")
    client.run("install .")

    rmdir(os.path.join(client.cache_folder, "greetings"))
    rmdir(os.path.join(client.cache_folder, "misc"))

    client.run("test *")
    assert "3 passed" in client.out

    client.run("test greetings:hello-world")
    assert "1 passed" in client.out

    client.run("test misc:*")
    assert "1 passed" in client.out

    client.run("new editable:mycommand")
    client.run("install . -e")
    client.run("test editable:*")
    assert "1 passed" in client.out

    client.run("test *")
    assert "4 passed" in client.out
