from json import load, loads
from importlib import reload
from unittest.mock import PropertyMock

from requests.exceptions import HTTPError
from pytest import fixture, raises

import lumapps.api.utils as utils
import lumapps.api.client as client
from lumapps.api.errors import ApiCallError, ApiClientError


@fixture(autouse=True)
def reset_env():
    reload(utils)
    reload(client)


@fixture
def cli() -> client.ApiClient:
    c = client.ApiClient(token="foobar")
    with open("tests/test_data/lumapps_discovery.json") as fh:
        c._discovery_doc = load(fh)
    return c


def test_api_client_no_auth():
    a = client.ApiClient()
    with raises(ApiClientError):
        a.session


def test_api_client_token_setter():
    token = "bvazbduioanpdo2"
    cli = client.ApiClient(token=token)
    assert cli.token == token
    assert cli._headers is not None
    assert token in cli.session.headers["authorization"]


def test_get_call_raises_api_call_error(cli: client.ApiClient):
    with raises(ApiCallError):
        cli.get_call("foo")
    with raises(ApiCallError):
        cli.get_call("user/bla")


def test_endpoints_property(cli: client.ApiClient):
    assert ("user", "get") in cli.endpoints


def test_get_help(cli: client.ApiClient):
    h = cli.get_help(("user", "get"))
    assert "user get" in h
    with raises(KeyError):
        cli.get_help(("user", "get123"))
    h = cli.get_help(("user", "get"), debug=True)
    assert "user get" in h
    with raises(KeyError):
        cli.get_help(("user", "get123"), debug=True)


def test_get_matching_endpoints(cli: client.ApiClient):
    matches = cli.get_matching_endpoints(("user", "ge"))
    assert "not found" in matches
    matches = cli.get_matching_endpoints(("user",))
    assert "user list" in matches
    matches = cli.get_matching_endpoints(("xyz",))
    assert "not found" in matches


def test_get_api_call(mocker, cli: client.ApiClient):
    with raises(HTTPError):
        cli._get_api_call(("user", "get"), {})


def test_get_call_1(mocker, cli: client.ApiClient):
    with open("tests/test_data/community_1.json") as fh:
        community = load(fh)
    mocker.patch("lumapps.api.client.ApiClient._get_api_call", return_value=community)
    community2 = cli.get_call("community/get", uid="foo")
    assert community["id"] == community2["id"]


def test_get_call_2(mocker, cli: client.ApiClient):
    with open("tests/test_data/instance_list_more_1.json") as fh:
        ret1 = load(fh)
    with open("tests/test_data/instance_list_more_2.json") as fh:
        ret2 = load(fh)

    def _call(name_parts, params):
        if "cursor" in params:
            return ret2
        else:
            return ret1

    mocker.patch("lumapps.api.client.ApiClient._get_api_call", side_effect=_call)
    lst = cli.get_call("instance/list")
    assert len(lst) == 4


def test_get_call_3(mocker, cli: client.ApiClient):
    with open("tests/test_data/list_empty.json") as fh:
        ret = load(fh)
    mocker.patch("lumapps.api.client.ApiClient._get_api_call", return_value=ret)
    lst = cli.get_call("instance/list")
    assert len(lst) == 0


def test_extract_from_discovery(mocker, cli: client.ApiClient):
    r = cli._extract_from_discovery("foo")
    assert r == {}
    cli._discovery_doc.clear()
    r = cli._extract_from_discovery("foo")
    assert r is None


def test_iter_call_1(mocker, cli: client.ApiClient):
    with open("tests/test_data/instance_list.json") as fh:
        ret = load(fh)
    mocker.patch("lumapps.api.client.ApiClient._get_api_call", return_value=ret)
    lst = [i for i in cli.iter_call("instance/list")]
    assert len(lst) == 2


def test_iter_call_2(mocker, cli: client.ApiClient):
    with open("tests/test_data/instance_list_more_1.json") as fh:
        ret1 = load(fh)
    with open("tests/test_data/instance_list_more_2.json") as fh:
        ret2 = load(fh)

    def _call(name_parts, params):
        if "cursor" in params:
            return ret2
        else:
            return ret1

    mocker.patch("lumapps.api.client.ApiClient._get_api_call", side_effect=_call)
    lst = [i for i in cli.iter_call("instance/list")]
    assert len(lst) == 4


def test_iter_call_3(mocker, cli: client.ApiClient):
    with open("tests/test_data/list_empty.json") as fh:
        ret = load(fh)
    mocker.patch("lumapps.api.client.ApiClient._get_api_call", return_value=ret)
    lst = [i for i in cli.iter_call("instance/list")]
    assert len(lst) == 0


def test_prune(cli: client.ApiClient):
    with open("tests/test_data/content_1.json") as fh:
        content = load(fh)
    assert "lastRevision" in content
    cli._prune(("content", "get"), content)
    assert "lastRevision" in content
    cli.prune = True
    cli._prune(("content", "get"), content)
    assert "lastRevision" not in content


def test_prune2(cli: client.ApiClient):
    with open("tests/test_data/instance_list.json") as fh:
        lst = load(fh)["items"]
    utils.FILTERS["instance/list"] = ["status"]
    for inst in lst:
        assert "status" in inst
    cli._prune(("instance", "list"), lst)
    for inst in lst:
        assert "status" in inst
    cli.prune = True
    cli._prune(("instance", "list"), lst)
    for inst in lst:
        assert "status" not in inst


def test_with_proxy_1():
    c = client.ApiClient(
        token="foobar",
        proxy_info={
            "scheme": "http",
            "host": "foo.bar",
            "port": 123456,
        },
    )
    s = c.session
    assert len(s.proxies) == 2


def test_with_proxy_2():
    c = client.ApiClient(
        token="foobar",
        proxy_info={
            "scheme": "https",
            "host": "foo.bar",
            "port": 123456,
            "user": "jo",
            "password": "foopass",
        },
    )
    s = c.session
    assert len(s.proxies) == 2


def test_discovery_doc(mocker):
    mocker.patch(
        "lumapps.api.utils._get_conn", return_value=utils._get_conn(":memory:")
    )

    class DummyResp:
        def __init__(self, text):
            self.text = text

        def json(self):
            return loads(self.text)

    with open("tests/test_data/lumapps_discovery.json") as fh:
        resp = DummyResp(fh.read())

    class DummySession:

        def get(*args, **kwargs):
            return resp

    c = client.ApiClient(token="foobar")
    mocker.patch(
        "lumapps.api.client.ApiClient.session",
        new_callable=PropertyMock,
        return_value=DummySession(),
    )
    doc1 = c.discovery_doc
    c._discovery_doc = None
    doc2 = c.discovery_doc
    assert doc1
    assert doc1 == doc2


def test_get_new_client_as(mocker, cli: client.ApiClient):
    mocker.patch(
        "lumapps.api.client.ApiClient.get_call", return_value={"accessToken": "foo"}
    )
    new_cli = cli.get_new_client_as("foo@bar.com")
    assert new_cli.user == "foo@bar.com"


def test_get_new_client_as_using_dwd(mocker, cli: client.ApiClient):
    new_cli = cli.get_new_client_as_using_dwd("foo@bar.com")
    assert new_cli.user == "foo@bar.com"
