import pytest

from copy import deepcopy
from lumapps.api.client import pop_matches, ApiClient, _parse_method_parts


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
    assert d2 == d

    s = "not a dict"
    pth = "foo/bar"
    pop_matches(pth, s)
    l1 = ["a", "b"]
    l2 = deepcopy(l1)
    pop_matches(pth, l1)
    assert l2 == l1


def test_api_client_no_auth():
    with pytest.raises(Exception):
        ApiClient()


def test_api_client_token_setter():
    token = "bvazbduioanpdo2"
    client = ApiClient(token=token)
    assert client.creds is not None
    assert client.creds.token == token

def test_parse_method_parts():
    s = ("user/get", )
    parts = _parse_method_parts(s)
    assert parts == ["user", "get"]
