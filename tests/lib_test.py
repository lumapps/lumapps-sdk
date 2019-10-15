import pytest

from copy import deepcopy
from lumapps.api.client import pop_matches, ApiClient


def test_pop_matches():
    d = {"a": 1, "b": {"c": 2, "d": {"e": 3}}, "z": 33}

    d2 = deepcopy(d)
    pth = "b/d/e"
    pop_matches(pth, d2)
    assert d2 == {"a": 1, "b": {"c": 2, "d": {}}, "z": 33}

    d2 = deepcopy(d)
    pth = "b"
    pop_matches(pth, d2)
    assert d2 == {"a": 1, "z": 33}

    d2 = deepcopy(d)
    pth = ""
    pop_matches(pth, d2)
    assert d2 == {"a": 1, "b": {"c": 2, "d": {"e": 3}}, "z": 33}


def test_api_client_no_auth():
    with pytest.raises(Exception):
        ApiClient()


def test_api_client_token_setter():
    token = "bvazbduioanpdo2"
    client = ApiClient(token=token)
    assert client.creds is not None
    assert client.creds.token == token
