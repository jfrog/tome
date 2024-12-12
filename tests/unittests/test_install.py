import tempfile

import pytest
from tome.errors import TomeException
from tome.internal.source import Source, SourceType


@pytest.mark.parametrize(
    "source,expected_type",
    [
        ("https://github.com/jfrog/tome.git", "git"),
        ("git@github.com:jfrog/tome.git", "git"),
        ("git@github.com:jfrog/tome", "git"),
        ("https://github.com/jfrog/tome.git@main", "git"),
        ("myfolder/.git", "git"),
        ("myfolder/.git@main", "git"),
        (tempfile.mkdtemp(), "folder"),
        ("http://example.com/script.zip", "url"),
        ("https://example.com/repo.git", "git"),
        ("https://example.com/repo/foobar", "url"),
    ],
)
def test_get_type(source, expected_type):
    assert Source.parse(source).type is SourceType(expected_type)


@pytest.mark.parametrize("invalid_source", ["invalid_input", "ftp://example.com/file", "abcd.efg"])
def test_get_type_invalid(invalid_source):
    with pytest.raises(TomeException):
        Source.parse(invalid_source)
