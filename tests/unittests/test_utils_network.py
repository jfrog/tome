import os
import tempfile

import pytest
from requests import Response
from tome.errors import TomeException
from tome.internal.utils import files
from tome.internal.utils.network import FileDownloader
from tome.internal.utils.network import response_to_str


def test_check_checksum():
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    files.save(temp_file.name, "lentejas los viernes")
    FileDownloader.check_checksum(
        temp_file.name,
        md5="7eff4d328587d1e23899db39376c8696",
        sha1="3029ebe5720934bac62b88e28c8e9fb1a33f7d3d",
        sha256="e719d00dcab39d3a3c2557519dfa772d9b32b9faa81cc91b0fee0511df05489f",
    )
    with pytest.raises(TomeException):
        FileDownloader.check_checksum(temp_file.name, md5="foobar", sha1=None, sha256=None)
    temp_file.close()
    os.unlink(temp_file.name)


def test_response_to_str(mocker):
    response = Response()
    assert response_to_str(response) is None

    response._content = b"tenia el sobrenombre de quijada o quesada"
    assert response_to_str(response) == "tenia el sobrenombre de quijada o quesada"

    response.headers["content-type"] = "application/json"
    response._content = b'{"errors" : [ {"status" : 400, "message" : "algun palomino de anadidura los domingos"}]}'
    assert response_to_str(response) == "400: algun palomino de anadidura los domingos"

    response._content = b'{"invalid" : [ {"code" : 400, "text" : "Ops!"}]}'
    assert response_to_str(response) == '{"invalid" : [ {"code" : 400, "text" : "Ops!"}]}'

    response.headers["content-type"] = "text/html"
    response.status_code = 404
    response.reason = "Not Found"
    response._content = b"it should not show this message"
    assert response_to_str(response) == "404: Not Found"

    # Test safe-exception when decoding content
    response_mock = mocker.Mock(spec=Response)
    response_mock._content = mocker.Mock(return_value=b"Failure")
