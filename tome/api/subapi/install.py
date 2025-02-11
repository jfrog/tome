import os
import sys

import yaml

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

    def install_from_tomefile(self, tomefile, force_requirements, create_env):
        """
        sources:
        - origin: git@github.com:jfrog/tome.git
          verify_ssl: true
          sys:
          - darwin
          - linux
        """
        abs_tomefile = tomefile if os.path.isfile(tomefile) else os.path.abspath(tomefile)
        try:
            with open(abs_tomefile) as tf:
                tomefile = yaml.safe_load(tf.read())
        except Exception as error:
            raise TomeException(f'Cannot read: "{tomefile}"') from error
        summary = {'skipped': {}, 'installed': {}, 'failed': {}}
        for script in tomefile.get("sources", []):
            if not isinstance(script, dict):
                raise TomeException(f'Cannot parse source: "{script}"')
            origin = script.get("origin")
            if (not script.get("platform")) or (script.get("platform") and sys.platform in script.get("platform")):
                if origin.startswith("-e") or origin.startswith("--editable"):
                    summary['failed'][origin] = "Editable installation is not allowed in a tomefile"
                else:
                    source = Source.parse(origin)
                    source.verify_ssl = script.get("verify_ssl", True)
                    try:
                        self.install_from_source(source, force_requirements, create_env)
                        summary['installed'][origin] = sys.platform if script.get("platform") else ''
                    except TomeException as e:
                        summary['failed'][origin] = str(e)
            else:
                summary['skipped'][origin] = f"'{sys.platform}' not in {script.get('platform')}"
        return summary

    def install_editable(self, source, force_requirements, create_env):
        install_editable(source, self.tome_api.cache_folder, force_requirements, create_env)

    def uninstall_from_source(self, source):
        cache = Cache(self.tome_api.cache_folder)
        target_folder = cache.get_target_folder(source)
        uninstall_from_source(source.uri, self.tome_api.cache_folder, target_folder)

    def uninstall_from_tomefile(self, tomefile):
        abs_tomefile = tomefile if os.path.isfile(tomefile) else os.path.abspath(tomefile)
        try:
            with open(abs_tomefile) as tf:
                tomefile = yaml.safe_load(tf.read())
        except Exception as error:
            raise TomeException(f'Cannot read: "{tomefile}"') from error
        for script in tomefile.get("sources", []):
            origin = script.get("origin")
            if (not script.get("platform")) or (script.get("platform") and sys.platform in script.get("platform")):
                if origin.startswith("-e") or origin.startswith("--editable"):
                    continue
                try:
                    source = Source.parse(origin)
                    self.uninstall_from_source(source)
                except TomeException:
                    pass
