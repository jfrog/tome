import os

from tome.internal.utils.files import short_hash_path


class TomePaths:
    """pure computing of paths in the home, not caching anything"""

    def __init__(self, cache_folder):
        self._cache_base_folder = cache_folder

    @property
    def scripts_path(self):
        scripts_path = os.path.join(self._cache_base_folder, "scripts")
        if not os.path.isdir(scripts_path):
            os.makedirs(scripts_path)
        return scripts_path

    @property
    def editables_path(self):
        return os.path.join(self._cache_base_folder, "tome_editables.json")


class Cache:
    def __init__(self, cache_folder):
        self.cache_folder = cache_folder
        self.paths = TomePaths(self.cache_folder)

    # FIXME: this needs to be handled better or we can
    #  get multiple copies of the same thing in the cache
    #  also try to use folders that are recognizable
    def get_target_folder(self, source):
        hashed = short_hash_path(source.uri)
        return os.path.join(self.paths.scripts_path, hashed)
