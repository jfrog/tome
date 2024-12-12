import os
import sys
from pathlib import Path

import yaml

from tome.api.subapi.install import InstallApi
from tome.api.subapi.list import ListApi
from tome.errors import TomeException
from tome.internal.utils.files import load
from tome.internal.vault.basic import VaultApi


def get_tome_home(home=None, base_home='~'):
    if home:
        return home

    def _find_tomews_file():
        path = Path(os.getcwd())
        while path.is_dir() and len(path.parts) > 1:  # finish at '/'
            tomews_yml = path / "tomews.yml"
            if tomews_yml.is_file():
                return tomews_yml
            else:
                path = path.parent

    ws_file = _find_tomews_file()
    ws_home = None
    if ws_file:
        ws = yaml.safe_load(load(ws_file))
        ws_home = ws.get("home")
        ws_home = os.path.abspath(os.path.join(os.path.dirname(ws_file), ws_home)) if ws_home else None
    home = ws_home or os.getenv("TOME_HOME") or os.path.join(os.path.expanduser(base_home), '.tome')
    return home


class _StoreAPI:
    def __init__(self, folder):
        self.folder = folder


class TomeAPI:
    def __init__(self, cache_folder=None):
        # TODO: Is it enough with the pyproject.toml declaration?
        if sys.version_info < (3, 8):  # os.path.expanduser needs 3.8 in Windows
            raise TomeException("tome needs at least Python 3.8 to run")

        home = get_tome_home(cache_folder)
        self.cache_folder = home
        if not os.path.isabs(self.cache_folder):
            raise TomeException(f"Invalid Tome home: {self.cache_folder}, it should be an absolute path")
        self.store = _StoreAPI(os.path.join(self.cache_folder, 'storage'))
        self.vault = VaultApi(self.cache_folder)
        # APIs declaration
        self.list = ListApi(self)
        self.install = InstallApi(self)
