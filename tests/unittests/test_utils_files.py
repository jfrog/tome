import os
import tempfile

import pytest
from tests.utils.files import temp_folder
from tome.errors import TomeException
from tome.internal.utils import files


def test_rmdir():
    """Test that the rmdir function removes a directory and its contents.
    When passing a file path, the function should remove not remove the file.
    """
    temp_folder_path = temp_folder()
    test_file_path = os.path.join(temp_folder_path, "test.file")
    files.save(test_file_path, "foobar")
    files.rmdir(test_file_path)
    assert os.path.exists(test_file_path)
    files.rmdir(temp_folder_path)
    assert not os.path.exists(temp_folder_path)


def test_renamedir():
    temp_folder_path = temp_folder()
    new_dir_name = temp_folder_path + "_new"
    files.renamedir(temp_folder_path, new_dir_name)
    assert not os.path.exists(temp_folder_path)
    assert os.path.exists(new_dir_name)


def test_chdir():
    temp_folder_path = temp_folder()
    with files.chdir(temp_folder_path):
        assert temp_folder_path in os.getcwd()
    assert os.getcwd() != temp_folder_path


def test_sha1():
    assert files.sha1(b"test") == "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3"
    assert files.sha1(None) is None


def test_sha256():
    assert files.sha256(b"test") == "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
    assert files.sha256(None) is None


def test_copy_file():
    temp_folder_path = temp_folder()
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    files.copy_file(temp_file.name, temp_folder_path)
    assert os.path.exists(os.path.join(temp_folder_path, temp_file.name))
    temp_file.close()
    os.unlink(temp_file.name)


def test_check_with_algorithm_sum():
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(b"test")
    with pytest.raises(TomeException):
        files.check_with_algorithm_sum("sha1", temp_file.name, "invalid_signature")
    with pytest.raises(TomeException):
        files.check_with_algorithm_sum("sha256", temp_file.name, "invalid_signature")
    files.check_with_algorithm_sum("sha1", temp_file.name, "da39a3ee5e6b4b0d3255bfef95601890afd80709")
    files.check_with_algorithm_sum(
        "sha256", temp_file.name, "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
    )
    temp_file.close()
    os.unlink(temp_file.name)


def test_save_and_load():
    temp_folder_path = temp_folder()
    file_path = os.path.join(temp_folder_path, "test.file")
    files.save(file_path, "foobar qux")
    assert files.load(file_path) == "foobar qux"


def test_save_files():
    temp_folder_path = temp_folder()
    files.save_files(
        temp_folder_path,
        {
            "test1.file": "foo bar",
            "test2.file": "qux baz",
        },
    )
    assert files.load(os.path.join(temp_folder_path, "test1.file")) == "foo bar"
    assert files.load(os.path.join(temp_folder_path, "test2.file")) == "qux baz"


def test_mkdir():
    temp_folder_path = temp_folder()
    new_dir = os.path.join(temp_folder_path, "foobar")
    files.mkdir(new_dir)
    assert os.path.isdir(new_dir)


def test_human_size():
    assert files.human_size("12") == "12B"
    assert files.human_size("22000") == "22.0KB"
    assert files.human_size("12825400") == "12.8MB"
    assert files.human_size("2490000222") == "2.49GB"
    assert files.human_size("5523200000222") == "5.52TB"
    assert files.human_size("7845523200000222") == "7.85PB"


def test_is_subdirectory():
    temp_folder_path = temp_folder()
    subfolder = os.path.join(temp_folder_path, "sub")
    assert files.is_subdirectory(subfolder, temp_folder_path)
    assert not files.is_subdirectory(temp_folder_path, subfolder)
