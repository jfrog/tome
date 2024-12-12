import os
import pytest


@pytest.fixture(scope="session", autouse=True)
def tests_setup_and_teardown():
    home = os.environ.get("TOME_HOME")
    if home:
        del os.environ["TOME_HOME"]
    yield
    if home:
        os.environ["TOME_HOME"] = home
