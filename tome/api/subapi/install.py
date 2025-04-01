from tome.internal.cache import Cache
from tome.internal.installer import install_editable, install_from_source, uninstall_from_source


class InstallApi:
    def __init__(self, tome_api):
        self.tome_api = tome_api

    def install_from_source(self, source, force_requirements, create_env):
        cache = Cache(self.tome_api.cache_folder)
        target_folder = cache.get_target_folder(source)
        return install_from_source(source, target_folder, force_requirements, create_env)

    def install_editable(self, source, force_requirements, create_env):
        return install_editable(source, self.tome_api.cache_folder, force_requirements, create_env)

    def uninstall_from_source(self, source):
        cache = Cache(self.tome_api.cache_folder)
        target_folder = cache.get_target_folder(source)
        return uninstall_from_source(source, self.tome_api.cache_folder, target_folder)
