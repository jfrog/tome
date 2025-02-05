import os
from enum import Enum

from tome.errors import TomeException


class SourceType(Enum):
    GIT = "git"  # git clone (no matter if local or remote)
    URL = "url"  # downloading a zipped tarball
    FOLDER = "folder"
    EDITABLE = "editable"
    FILE = "file"

    def __str__(self):
        return self.value


class Source:
    def __init__(self, url, source_type, version, verify_ssl, commit, folder=None):
        self.url = url
        self.type = source_type
        self.version = version
        self.verify_ssl = verify_ssl
        self.commit = commit
        self.folder = folder

    def __str__(self):
        return self.url

    def serialize(self):
        return {
            "url": self.url,
            "type": str(self.type),
            "version": self.version,
            "verify_ssl": self.verify_ssl,
            "commit": self.commit,
            "folder": self.folder,
        }

    @staticmethod
    def deserialize(data):
        return Source(
            data["url"], SourceType(data["type"]), data["version"], data["verify_ssl"], data["commit"], data["folder"]
        )

    @staticmethod
    def parse(source):
        if not source:
            raise TomeException("No installation source provided.")
        if ".git" in source or source.startswith("git@"):
            source_type = SourceType.GIT
            if ".git@" in source:
                url, _, version = source.rpartition("@")
            else:
                url, version = source, None
            verify_ssl = True
        elif source.startswith("http"):
            source_type = SourceType.URL
            url, version, verify_ssl = source, None, True
        else:
            source = os.path.abspath(source)
            if os.path.isdir(source):
                source_type = SourceType.FOLDER
                url, version, verify_ssl = source, None, None
            elif os.path.isfile(source):
                source_type = SourceType.FILE
                url, version, verify_ssl = source, None, None
            else:
                raise TomeException(f"Could not determine the type for source: {source}")

        return Source(url, source_type, version, verify_ssl, None, None)
