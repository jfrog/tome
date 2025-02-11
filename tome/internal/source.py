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
    def __init__(self, uri, source_type, version, verify_ssl, commit, folder=None):
        self.uri = uri
        self.type = source_type
        self.version = version
        self.verify_ssl = verify_ssl
        self.commit = commit
        self.folder = folder

    def __str__(self):
        return self.uri

    def serialize(self):
        return {
            "uri": self.uri,
            "type": str(self.type),
            "version": self.version,
            "verify_ssl": self.verify_ssl,
            "commit": self.commit,
            "folder": self.folder,
        }

    @staticmethod
    def deserialize(data):
        return Source(
            data["uri"], SourceType(data["type"]), data["version"], data["verify_ssl"], data["commit"], data["folder"]
        )

    @staticmethod
    def parse(source):
        if not source:
            raise TomeException("No installation source provided.")
        if ".git" in source or source.startswith("git@"):
            source_type = SourceType.GIT
            if ".git@" in source:
                uri, _, version = source.rpartition("@")
            else:
                uri, version = source, None
            verify_ssl = True
        elif source.startswith("http"):
            source_type = SourceType.URL
            uri, version, verify_ssl = source, None, True
        else:
            source = os.path.abspath(source)
            if os.path.isdir(source):
                source_type = SourceType.FOLDER
                uri, version, verify_ssl = source, None, None
            elif os.path.isfile(source):
                source_type = SourceType.FILE
                uri, version, verify_ssl = source, None, None
            else:
                raise TomeException(f"Could not determine the type for source: {source}")

        return Source(uri, source_type, version, verify_ssl, None, None)
