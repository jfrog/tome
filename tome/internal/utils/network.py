import json
from pathlib import Path

import requests
from requests.auth import HTTPBasicAuth
from rich.progress import Progress
from tome.api.output import TomeOutput
from tome.errors import AuthenticationException
from tome.errors import ForbiddenException
from tome.errors import NotFoundException
from tome.errors import TomeException
from tome.internal.utils.files import check_with_algorithm_sum


def response_to_str(response: requests.Response) -> str:
    content = response.content
    try:
        # A bytes message, decode it as str
        if isinstance(content, bytes):
            content = content.decode()

        content_type = response.headers.get("content-type") or ""

        if content_type == "application/json":
            # Errors from Artifactory looks like:
            #  {"errors" : [ {"status" : 400, "message" : "Bla bla bla"}]}
            try:
                data = json.loads(content)["errors"][0]
                content = "{}: {}".format(data["status"], data["message"])
            except Exception as error:
                TomeOutput().warning(f"Failed to parse JSON response: {error}")
        elif "text/html" in content_type:
            content = f"{response.status_code}: {response.reason}"

        return content

    except Exception:
        return response.content


class Requester:
    def __init__(self):
        """Initializes a new Requester instance with a persistent HTTP session."""
        self.session = requests.Session()

    def get(self, url, stream=False, verify=True, auth=None, headers=None):
        """
        Performs a GET request.

        :param url: URL for the request.
        :param stream: Whether to stream the response.
        :param verify: Whether to verify SSL certificates.
        :param auth: Authentication tuple (username, password) or None.
        :param headers: Dictionary of HTTP headers.
        :return: Response object from the request.
        """
        if auth:
            auth = HTTPBasicAuth(*auth)

        response = self.session.get(url, stream=stream, verify=verify, auth=auth, headers=headers)
        return response


class FileDownloader:
    def __init__(self):
        self._output = TomeOutput()
        self._requester = Requester()

    def download(
        self,
        url,
        file_path,
        verify_ssl=True,
        auth=None,
        overwrite=False,
        headers=None,
        md5=None,
        sha1=None,
        sha256=None,
    ):
        file_path = Path(file_path)
        if file_path.exists() and not overwrite:
            raise TomeException(f"Error, the file to download already exists: '{file_path}'")
        try:
            self._download_file(url, auth, headers, file_path, verify_ssl)
            self.check_checksum(file_path, md5, sha1, sha256)
        except Exception as e:
            if file_path.exists():
                file_path.unlink()
            raise e

    def _download_file(self, url, auth, headers, file_path, verify_ssl):
        response = self._requester.get(url, stream=True, verify=verify_ssl, auth=auth, headers=headers)
        if not response.ok:
            if response.status_code == 404:
                raise NotFoundException("Not found: %s" % url)
            elif response.status_code == 403:
                if auth is None or (hasattr(auth, "token") and auth.token is None):
                    # TODO: This is a bit weird, why this conversion? Need to investigate
                    raise AuthenticationException(response_to_str(response))
                raise ForbiddenException(response_to_str(response))
            elif response.status_code == 401:
                raise AuthenticationException()
            raise TomeException("Error %d downloading file %s" % (response.status_code, url))

        total_size = int(response.headers.get('content-length', 0))
        with Progress() as progress:
            task = progress.add_task("[cyan]Downloading...", total=total_size)
            with open(file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=1024):
                    file.write(chunk)
                    progress.update(task, advance=len(chunk))

    @staticmethod
    def check_checksum(file_path, md5, sha1, sha256):
        if md5 is not None:
            check_with_algorithm_sum("md5", file_path, md5)
        if sha1 is not None:
            check_with_algorithm_sum("sha1", file_path, sha1)
        if sha256 is not None:
            check_with_algorithm_sum("sha256", file_path, sha256)
