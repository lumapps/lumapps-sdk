from json import load, loads
from unittest.mock import PropertyMock
from typing import Sequence

from httpx import HTTPError
from pytest import fixture, raises

from lumapps.api.client import ApiClient
from lumapps.api.utils import (
    FILTERS,
    _DiscoveryCacheDict,
    _set_sqlite_ok,
    _get_conn,
    get_discovery_cache,
)
from lumapps.api.errors import ApiCallError, ApiClientError


@fixture(autouse=True)
def reset_env():
    _DiscoveryCacheDict._cache.clear()
    _set_sqlite_ok(True)


@fixture
def cli() -> ApiClient:
    c = ApiClient(token="foobar")
    with open("tests/test_data/lumapps_discovery.json") as fh:
        doc = load(fh)
    # c.api_info = {"base_url": doc["baseUrl"]}
    get_discovery_cache().set(doc["baseUrl"], doc)
    return c


@fixture
def cli_drive() -> ApiClient:
    with open("tests/test_data/drive_v3_discovery.json") as fh:
        doc = load(fh)
    get_discovery_cache().set(doc["baseUrl"], doc)
    c = ApiClient(token="foobar", api_info={
        "base_url": "https://www.googleapis.com",
        "name": "drive",
        "version": "v3",
        "scopes": ["https://www.googleapis.com/auth/drive"],
    })
    return c


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


def test_set_get_token(cli: ApiClient):
    cli.token = "foo123"
    assert cli.token == "foo123"
    cli.token = "foo123"
    assert cli.token == "foo123"
    _ = cli.session
    cli.token = "foo1234"
    assert cli.token == "foo1234"


def test_endpoints_property(cli: ApiClient):
    assert ("user", "get") in cli.endpoints


def test_get_help(cli: ApiClient):
    h = cli.get_help(("user", "get"))
    assert "user get" in h
    with raises(KeyError):
        cli.get_help(("user", "get123"))
    h = cli.get_help(("user", "get"), debug=True)
    assert "user get" in h
    with raises(KeyError):
        cli.get_help(("user", "get123"), debug=True)


def test_get_matching_endpoints(cli: ApiClient):
    matches = cli.get_matching_endpoints(("user", "ge"))
    assert "not found" in matches
    matches = cli.get_matching_endpoints(("user",))
    assert "user list" in matches
    matches = cli.get_matching_endpoints(("xyz",))
    assert "not found" in matches


def test_call_1(mocker, cli: ApiClient):
    with raises(HTTPError):
        cli._call(("user", "get"), {})


def test_call_2(mocker, cli: ApiClient):
    class DummyResp:
        def __init__(self):
            self.content = None

        def raise_for_status(self):
            pass

    class DummySession:
        def __init__(self):
            pass

        def request(self, *args, **kwargs):
            return DummyResp()

    mocker.patch(
        "lumapps.api.client.ApiClient.session",
        new_callable=PropertyMock,
        return_value=DummySession(),
    )
    assert cli._call(("user", "get"), {}) is None


def test_get_verb_path_params(mocker, cli_drive: ApiClient):
    with raises(ApiCallError):
        cli_drive._get_verb_path_params(("permissions", "list"), {})
    verb, path, params = cli_drive._get_verb_path_params(
        ("permissions", "list"), {"fileId": "foo_id"}
    )
    assert verb == "GET"
    assert len(params) == 0


def test_get_call_1(mocker, cli: ApiClient):
    with open("tests/test_data/community_1.json") as fh:
        community = load(fh)
    mocker.patch("lumapps.api.client.ApiClient._call", return_value=community)
    community2 = cli.get_call("community/get", uid="foo")
    assert community["id"] == community2["id"]


def test_get_call_2(mocker, cli: ApiClient):
    with open("tests/test_data/instance_list_more_1.json") as fh:
        ret1 = load(fh)
    with open("tests/test_data/instance_list_more_2.json") as fh:
        ret2 = load(fh)

    def _call(name_parts: Sequence[str], params: dict, json=None):
        if "cursor" in params:
            return ret2
        else:
            return ret1

    mocker.patch("lumapps.api.client.ApiClient._call", side_effect=_call)
    lst = cli.get_call("instance/list")

    assert cli.cursor is None
    assert len(lst) == 4


def test_get_call_3(mocker, cli: ApiClient):
    with open("tests/test_data/list_empty.json") as fh:
        ret = load(fh)
    mocker.patch("lumapps.api.client.ApiClient._call", return_value=ret)
    lst = cli.get_call("instance/list")
    assert len(lst) == 0


def test_get_call_4(mocker, cli: ApiClient):
    with open("tests/test_data/list_empty.json") as fh:
        ret = load(fh)
    mocker.patch("lumapps.api.client.ApiClient._call", return_value=ret)
    lst = cli.get_call("instance/list", cursor="test")

    assert len(lst) == 0
    assert cli.cursor is None


def test_get_call_5(mocker, cli: ApiClient):
    try:
        cli.get_call("instance/list", cursor="test")
    except Exception:
        assert cli.cursor == "test"


def test_get_call_6(mocker, cli: ApiClient):
    with open("tests/test_data/instance_list_more_1.json") as fh:
        ret1 = load(fh)

    def _call(name_parts: Sequence[str], params: dict, json=None):
        if "cursor" in params:
            raise Exception()
        else:
            return ret1

    mocker.patch("lumapps.api.client.ApiClient._call", side_effect=_call)
    try:
        cli.get_call("instance/list")
    except Exception:
        assert cli.cursor == "foo_cursor"


def test_iter_call_1(mocker, cli: ApiClient):
    with open("tests/test_data/instance_list.json") as fh:
        ret = load(fh)
    mocker.patch("lumapps.api.client.ApiClient._call", return_value=ret)

    lst = [i for i in cli.iter_call("instance/list")]
    assert len(lst) == 2


def test_iter_call_2(mocker, cli: ApiClient):
    with open("tests/test_data/instance_list_more_1.json") as fh:
        ret1 = load(fh)
    with open("tests/test_data/instance_list_more_2.json") as fh:
        ret2 = load(fh)

    def _call(name_parts: Sequence[str], params: dict, json=None):
        if "cursor" in params:
            return ret2
        else:
            return ret1

    mocker.patch("lumapps.api.client.ApiClient._call", side_effect=_call)
    lst = [i for i in cli.iter_call("instance/list")]
    assert len(lst) == 4


def test_iter_call_3(mocker, cli: ApiClient):
    with open("tests/test_data/list_empty.json") as fh:
        ret = load(fh)
    mocker.patch("lumapps.api.client.ApiClient._call", return_value=ret)
    lst = [i for i in cli.iter_call("instance/list")]
    assert len(lst) == 0


def test_iter_call_4(mocker, cli: ApiClient):
    with open("tests/test_data/instance_list.json") as fh:
        ret = load(fh)
    mocker.patch("lumapps.api.client.ApiClient._call", return_value=ret)

    lst = [i for i in cli.iter_call("instance/list", cursor="truc")]
    assert len(lst) == 2
    assert cli.cursor is None


def test_iter_call_5(mocker, cli: ApiClient):
    with open("tests/test_data/instance_list_more_1.json") as fh:
        ret1 = load(fh)
    with open("tests/test_data/instance_list_more_2.json") as fh:
        ret2 = load(fh)

    def _call(name_parts: Sequence[str], params: dict, json=None):
        if "cursor" in params:
            return ret2
        else:
            return ret1

    mocker.patch("lumapps.api.client.ApiClient._call", side_effect=_call)
    iterator = cli.iter_call("instance/list")

    # 1st page, cursor is set
    lst = next(iterator)
    assert isinstance(lst, dict)
    assert cli.cursor == "foo_cursor"
    lst = next(iterator)
    assert isinstance(lst, dict)
    assert cli.cursor == "foo_cursor"

    # 2nd page, cursor is none
    lst = next(iterator)
    assert isinstance(lst, dict)
    assert cli.cursor is None
    lst = next(iterator)
    assert isinstance(lst, dict)
    assert cli.cursor is None

    # Assert iterator ended
    with raises(StopIteration):
        next(iterator)

    lst = [i for i in cli.iter_call("instance/list")]
    assert len(lst) == 4
    assert cli.cursor is None


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


def test_with_proxy_1():
    c = ApiClient(
        token="foobar",
        proxy_info={"scheme": "http", "host": "foo.bar.com", "port": 12345},
    )
    s = c.session
    assert len(s.proxies) == 2


def test_with_proxy_2():
    c = ApiClient(
        token="foobar",
        proxy_info={
            "scheme": "https",
            "host": "foo.bar",
            "port": 12345,
            "user": "jo",
            "password": "foopass",
        },
    )
    s = c.session
    assert len(s.proxies) == 2


def test_discovery_doc(mocker):
    mocker.patch(
        "lumapps.api.utils._get_conn", return_value=_get_conn(":memory:")
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

    c = ApiClient(token="foobar")
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


def test_get_new_client_as(mocker, cli: ApiClient):
    mocker.patch(
        "lumapps.api.client.ApiClient.get_call",
        return_value={"accessToken": "foo"},
    )
    new_cli = cli.get_new_client_as("foo@bar.com")
    assert new_cli.user == "foo@bar.com"


def test_get_new_client_as_using_dwd(mocker, cli: ApiClient):
    new_cli = cli.get_new_client_as_using_dwd("foo@bar.com")
    assert new_cli.user == "foo@bar.com"
