import sys

from tests.utils.tools import TestClient


def test_new():
    client = TestClient()
    client.run("new mynamespace:mycommand")
    client.run("install .")
    client.run("list")
    assert "mynamespace:mycommand" in client.out
    client.run("mynamespace:mycommand arg1 --optional-argument arg2")
    assert "Tome command called with positional argument: arg1" in client.out
    assert "Tome command called with optional argument: arg2" in client.out


def test_new_tomeignore():
    client = TestClient()
    client.save({".DS_Store": "", "Thumbs.db": "", ".Trash-1000": ""})
    client.run("new mynamespace:mycommand")
    client.run("install .")
    assert "Copied ./.DS_Store" not in client.out
    assert "Copied ./Thumbs.db" not in client.out
    assert "Copied ./.Trash-1000" not in client.out


def test_new_oneliner_script():
    client = TestClient()
    script_type = "sh"
    if sys.platform == "win32":
        script_type = "bat"
    client.run("new mynamespace:mycommand --type " + script_type)
    client.run("install .")
    # testing this way because client.run wont return the things outputed by echo
    client.run("list")
    assert "mynamespace:mycommand      Description of the command." in client.out
    client.run("mynamespace:mycommand")  # it runs without failing


def test_new_oneliner_script_other():
    # It used to fail when there were other .py command in the same namespace
    client = TestClient()
    client.run("new mynamespace:mycmd")
    client.save({"otherscript.bat": "", "myshellscript.sh": ""})
    script_type = "sh"
    if sys.platform == "win32":
        script_type = "bat"
    client.run("new mynamespace:mycommand --type " + script_type)
    client.run("install .")
    # testing this way because client.run wont return the things outputed by echo
    client.run("list")
    assert "otherscript" not in client.out
    assert "myshellscript" not in client.out
    assert "mynamespace:mycommand      Description of the command." in client.out
    client.run("mynamespace:mycommand")  # it runs without failing


def test_new_with_hyphen():
    client = TestClient()
    client.run("new my-namespace:my-command")
    client.run("install .")
    client.run("list")
    assert "my-namespace:my-command" in client.out


def test_new_command_with_description():
    c = TestClient()
    c.run('new myspace:mycommand --description="This is a test command"')
    c.run("install .")
    c.run("list")
    assert "This is a test command" in c.out


class TestErrors:
    def test_new_no_namespace(self):
        c = TestClient()
        c.run("new mycommand", assert_error=True)
        assert "Error: Commands must be in the form namespace:command" in c.out

    def test_new_toomany_namespace(self):
        c = TestClient()
        c.run("new myspace:mycommand:other", assert_error=True)
        assert "Error: Commands must be in the form namespace:command" in c.out

    def test_existing_overwrite(self):
        c = TestClient()
        c.run("new myspace:mycommand")
        c.run("new myspace:mycommand", assert_error=True)
        assert "already exist. Use -f/--force" in c.out
        c.run("new myspace:mycommand -f")  # will not error
