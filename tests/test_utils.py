import json
from copy import deepcopy
from datetime import datetime, timedelta

from pytest import fixture

import lumapps.api.utils


@fixture(autouse=True)
def reset_env():
    lumapps.api.utils._DiscoveryCacheDict._cache.clear()
    lumapps.api.utils._set_sqlite_ok(True)


def test_list_prune_filters(capsys):
    lumapps.api.utils.list_prune_filters()
    captured = capsys.readouterr()
    assert captured.out.startswith("PRUNE FILTERS:")


def test_discovery_cache_1():
    assert type(lumapps.api.utils.DiscoveryCache) == lumapps.api.utils.DiscoveryCacheSqlite


def test_discovery_cache_dict():
    c = lumapps.api.utils._DiscoveryCacheDict
    assert c.get("foobar.com") is None
    c.set("foobar.com", "bla")
    assert c.get("foobar.com") == "bla"
    c._cache["foobar.com"]["expiry"] = datetime.now() - timedelta(days=100)
    assert c.get("foobar.com") is None


def test_discovery_cache_sqlite(mocker):
    conn = lumapps.api.utils._get_conn(":memory:")
    mocker.patch("lumapps.api.utils._get_conn", return_value=conn)
    c = lumapps.api.utils.DiscoveryCacheSqlite()
    assert c.get("foobar.com") is None
    c.set("foobar.com", "bla")
    assert c.get("foobar.com") == "bla"
    dt = (datetime.now() - timedelta(days=100)).isoformat()[:19]
    conn.execute(
        "UPDATE discovery_cache SET expiry=? WHERE url='foobar.com'", (dt, )
    )
    assert c.get("foobar.com") is None


def test_get_set_configs(mocker):
    mocker.patch(
        "lumapps.api.utils._get_conn",
        return_value=lumapps.api.utils._get_conn(":memory:"),
    )
    assert lumapps.api.utils._get_sqlite_ok() is True
    store = lumapps.api.utils.ConfigStore
    assert len(store.get_names()) == 0
    store.set("foo", "bar")
    assert len(store.get_names()) == 1
    store.set("foo", "bar")
    assert len(store.get_names()) == 1
    store.set("foo1", "bar1")
    assert len(store.get_names()) == 2
    assert store.get("foo") == "bar"


def test_no_sqlite(mocker):
    mocker.patch("lumapps.api.utils._get_sqlite_ok", return_value=False)
    c = lumapps.api.utils.DiscoveryCacheSqlite()
    assert c.get("foobar.com") is None
    c.set("foobar.com", "bla")
    assert c.get("foobar.com") == "bla"
    assert lumapps.api.utils.DiscoveryCache.get("foobar.com") == "bla"
    assert lumapps.api.utils._DiscoveryCacheDict.get("foobar.com") == "bla"


def test_parse_endpoint_parts():
    s = ("user/get",)
    parts = lumapps.api.utils._parse_endpoint_parts(s)
    assert parts == ["user", "get"]


def test_extract_from_discovery_spec():
    with open("tests/test_data/lumapps_discovery.json") as fh:
        discovery_doc = json.load(fh)
    name_parts = ["user", "get"]
    resources = discovery_doc["resources"]
    extracted = lumapps.api.utils._extract_from_discovery_spec(resources, name_parts)

    assert extracted.get("httpMethod") == "GET"
    assert extracted.get("id") == "lumsites.user.get"


def test_pop_matches():
    pop_matches = lumapps.api.utils.pop_matches
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
