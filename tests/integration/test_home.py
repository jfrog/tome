import json
import os
import textwrap

from tests.utils.files import temp_folder
from tests.utils.tools import TestClient, environment_update
from tome.api.api import TomeAPI
from tome.internal.utils.files import save, chdir, mkdir


def test_api_env():
    cache_folder = os.path.join(temp_folder(), "custom")
    with environment_update({"TOME_HOME": cache_folder}):
        api = TomeAPI()
        assert api.cache_folder == cache_folder


def test_config_home():
    c = TestClient()
    c.run("config home")
    assert c.cache_folder in c.stdout


def test_config_home_env():
    tmp = temp_folder()
    with environment_update({"TOME_HOME": tmp}):
        c = TestClient()
        c.run("config home")
        assert tmp in c.stdout


def test_config_home_tomews():
    tmp = temp_folder()
    home = os.path.join(tmp, "myhome")
    tomews = textwrap.dedent(f"""\
        home: ./myhome
    """)
    save(os.path.join(tmp, "tomews.yml"), tomews)
    cwd = os.path.join(tmp, "mycwd")
    mkdir(cwd)
    with chdir(cwd):
        c = TestClient()
        c.run("config home")
        assert home in c.stdout

        # The ws definition has higher priority than env-var
        tmp = temp_folder()
        with environment_update({"TOME_HOME": tmp}):
            c = TestClient()
            c.run("config home")
            assert home in c.stdout
