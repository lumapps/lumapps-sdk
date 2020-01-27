from json import load
from copy import deepcopy

from pytest import fixture, raises

from lumapps.api.client import pop_matches, ApiClient
from lumapps.api.utils import FILTERS
from lumapps.api.errors import ApiCallError, ApiClientError


@fixture
def cli() -> ApiClient:
    c = ApiClient(token="foobar")
    with open("tests/test_data/lumapps_discovery.json") as fh:
        c._discovery_doc = load(fh)
    return c


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
    a = ApiClient()
    with raises(ApiClientError):
        a.session


def test_api_client_token_setter():
    token = "bvazbduioanpdo2"
    client = ApiClient(token=token)
    assert client.token == token
    assert client._headers is not None
    assert token in client.session.headers["authorization"]


def test_get_call_raises_api_call_error(cli: ApiClient):
    with raises(ApiCallError):
        cli.get_call("foo")
    with raises(ApiCallError):
        cli.get_call("user/bla")


def test_endpoints_property(cli: ApiClient):
    assert ("user", "get") in cli.endpoints


def test_get_help(cli: ApiClient):
    h = cli.get_help(("user", "get"))
    assert "user get" in h
    with raises(KeyError):
        cli.get_help(("user", "get123"))


def test_get_matching_endpoints(cli: ApiClient):
    matches = cli.get_matching_endpoints(("user", "ge"))
    assert "not found" in matches
    matches = cli.get_matching_endpoints(("user",))
    assert "user list" in matches
    matches = cli.get_matching_endpoints(("xyz",))
    assert "not found" in matches


def test_get_call(mocker, cli: ApiClient):
    with open("tests/test_data/community_1.json") as fh:
        community = load(fh)
    mocker.patch(
        "lumapps.api.client.ApiClient._get_api_call", return_value=community
    )
    community2 = cli.get_call("community/get", uid="foo")
    assert community["id"] == community2["id"]


def test_iter_call(mocker, cli: ApiClient):
    with open("tests/test_data/instance_list.json") as fh:
        ret = load(fh)
    mocker.patch(
        "lumapps.api.client.ApiClient._get_api_call", return_value=ret
    )
    lst = [i for i in cli.iter_call("instance/list")]
    assert len(lst) == 2


def test_prune(cli: ApiClient):
    with open("tests/test_data/content_1.json") as fh:
        content = load(fh)
    assert "lastRevision" in content
    cli._prune(("content", "get"), content)
    assert "lastRevision" in content
    cli.prune = True
    cli._prune(("content", "get"), content)
    assert "lastRevision" not in content


def test_prune2(cli: ApiClient):
    with open("tests/test_data/instance_list.json") as fh:
        lst = load(fh)["items"]
    FILTERS["instance/list"] = ["status"]
    for inst in lst:
        assert "status" in inst
    cli._prune(("instance", "list"), lst)
    for inst in lst:
        assert "status" in inst
    cli.prune = True
    cli._prune(("instance", "list"), lst)
    for inst in lst:
        assert "status" not in inst
