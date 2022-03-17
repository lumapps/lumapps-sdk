import pytest

from .utils import DirectClient


@pytest.fixture(scope="session")
def vcr_config():
    return {
        "filter_headers": ["authorization"],
        "match_request_on": ["method", "path", "headers", "body", "query"],
    }


@pytest.fixture(scope="session")
def vcr_cassette_dir():
   return "tests/cassettes/"


@pytest.fixture(scope="session")
def client():
    return DirectClient()
