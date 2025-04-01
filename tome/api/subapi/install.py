import os
import sys

import yaml

from tome.api.output import TomeOutput
from tome.errors import TomeException
from tome.internal.cache import Cache
from tome.internal.installer import install_editable
from tome.internal.installer import install_from_source
from tome.internal.installer import uninstall_from_source
from tome.internal.source import Source


class InstallApi:
    def __init__(self, tome_api):
        self.tome_api = tome_api

    def install_from_source(self, source, force_requirements, create_env):
        cache = Cache(self.tome_api.cache_folder)
        # FIXME: we should use the same target folder if the repo is the same
        #  regardless of the branch
        target_folder = cache.get_target_folder(source)
        install_from_source(source, target_folder, force_requirements, create_env)

    def install_editable(self, source, force_requirements, create_env):
        install_editable(source, self.tome_api.cache_folder, force_requirements, create_env)

    def uninstall_from_source(self, source):
        cache = Cache(self.tome_api.cache_folder)
        target_folder = cache.get_target_folder(source)
        uninstall_from_source(source.uri, self.tome_api.cache_folder, target_folder)
