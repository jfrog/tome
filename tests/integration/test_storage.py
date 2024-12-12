import os
import textwrap

from tests.utils.files import temp_folder
from tests.utils.tools import TestClient
from tome.internal.utils.files import mkdir


def test_store_home():
    tmp = temp_folder()
    client = TestClient(cache_folder=tmp)

    client.run("config store")
    assert tmp in client.out


def test_store_access():
    client = TestClient()
    client.run("config store")
    store_path = client.stdout.strip()
    client.save({os.path.join(store_path, "asset.txt"): "Hello world!"})
    mkdir(os.path.join(client.current_folder, "mynamespace"))

    tome_script = textwrap.dedent("""
    from tome.command import tome_command
    from tome.api.output import TomeOutput

    @tome_command()
    def mycommand(tome_api, parser, *args):
        '''Saying hello tome.'''
        with open(tome_api.store.folder + '/asset.txt', 'r') as file:
            TomeOutput().info(file.read())
    """)
    client.save({os.path.join(client.current_folder, "mynamespace", "mycommand.py"): tome_script})
    client.run("install .")
    client.run("mynamespace:mycommand")
    assert "Hello world!" in client.stderr
