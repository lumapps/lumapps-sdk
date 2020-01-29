import json
from copy import deepcopy
from datetime import datetime, timedelta

from pytest import fixture

from lumapps.api.utils import (
    list_prune_filters,
    _DiscoveryCacheDict,
    _DiscoveryCacheSqlite,
    DiscoveryCache,
    ConfigStore,
    _parse_endpoint_parts,
    _extract_from_discovery_spec,
    pop_matches,
    _get_conn,
    _get_sqlite_ok,
    _set_sqlite_ok,
)


@fixture(autouse=True)
def reset_env():
    _DiscoveryCacheDict._cache.clear()
    _set_sqlite_ok(True)


def test_list_prune_filters(capsys):
    list_prune_filters()
    captured = capsys.readouterr()
    assert captured.out.startswith("PRUNE FILTERS:")


def test_discovery_cache_1():
    assert DiscoveryCache == _DiscoveryCacheSqlite


def test_discovery_cache_dict(mocker):
    mocker.patch("lumapps.api.utils._get_conn", return_value=_get_conn(":memory:"))
    c = _DiscoveryCacheDict
    assert c.get("foobar.com") is None
    c.set("foobar.com", "bla")
    assert c.get("foobar.com") == "bla"
    c._cache["foobar.com"]["expiry"] = datetime.now() - timedelta(days=100)
    assert c.get("foobar.com") is None


def test_discovery_cache_sqlite(mocker):
    conn = _get_conn(":memory:")
    mocker.patch("lumapps.api.utils._get_conn", return_value=conn)
    c = _DiscoveryCacheSqlite
    assert c.get("foobar.com") is None
    c.set("foobar.com", "bla")
    assert c.get("foobar.com") == "bla"
    dt = (datetime.now() - timedelta(days=100)).isoformat()[:19]
    conn.execute(
        "UPDATE discovery_cache SET expiry=? WHERE url='foobar.com'", (dt, )
    )
    assert c.get("foobar.com") is None


def test_get_set_configs(mocker):
    mocker.patch("lumapps.api.utils._get_conn", return_value=_get_conn(":memory:"))
    assert _get_sqlite_ok() is True
    assert len(ConfigStore.get_names()) == 0
    ConfigStore.set("foo", "bar")
    assert len(ConfigStore.get_names()) == 1
    ConfigStore.set("foo", "bar")
    assert len(ConfigStore.get_names()) == 1
    ConfigStore.set("foo1", "bar1")
    assert len(ConfigStore.get_names()) == 2
    assert ConfigStore.get("foo") == "bar"


def test_no_sqlite(capsys, mocker):
    mocker.patch("lumapps.api.utils._get_sqlite_ok", return_value=False)
    mocker.patch("lumapps.api.utils._get_conn", return_value=_get_conn(":memory:"))
    c = _DiscoveryCacheSqlite
    assert c.get("foobar.com") is None
    c.set("foobar.com", "bla")
    assert c.get("foobar.com") == "bla"
    assert _DiscoveryCacheDict.get("foobar.com") == "bla"


def test_parse_endpoint_parts():
    s = ("user/get",)
    parts = _parse_endpoint_parts(s)
    assert parts == ["user", "get"]


def test_extract_from_discovery_spec():
    with open("tests/test_data/lumapps_discovery.json") as fh:
        discovery_doc = json.load(fh)
    name_parts = ["user", "get"]
    resources = discovery_doc["resources"]
    extracted = _extract_from_discovery_spec(resources, name_parts)

    assert extracted.get("httpMethod") == "GET"
    assert extracted.get("id") == "lumsites.user.get"


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

    obj = "foo"
    pop_matches("foo/bar", obj)
    assert obj == "foo"
