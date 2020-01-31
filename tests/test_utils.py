import json
from copy import deepcopy
from datetime import datetime, timedelta
from importlib import reload

from pytest import fixture

import lumapps.api.utils as utils


@fixture(autouse=True)
def reset_env():
    reload(utils)


def test_list_prune_filters(capsys):
    utils.list_prune_filters()
    captured = capsys.readouterr()
    assert captured.out.startswith("PRUNE FILTERS:")


def test_discovery_cache_1():
    assert utils.DiscoveryCache == utils._DiscoveryCacheSqlite


def test_discovery_cache_dict(mocker):
    mocker.patch(
        "lumapps.api.utils._get_conn", return_value=utils._get_conn(":memory:")
    )
    c = utils._DiscoveryCacheDict
    assert c.get("foobar.com") is None
    c.set("foobar.com", "bla")
    assert c.get("foobar.com") == "bla"
    c._cache["foobar.com"]["expiry"] = datetime.now() - timedelta(days=100)
    assert c.get("foobar.com") is None


def test_discovery_cache_sqlite(mocker):
    conn = utils._get_conn(":memory:")
    mocker.patch("lumapps.api.utils._get_conn", return_value=conn)
    c = utils._DiscoveryCacheSqlite
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
        "lumapps.api.utils._get_conn", return_value=utils._get_conn(":memory:")
    )
    assert utils._get_sqlite_ok() is True
    assert len(utils.ConfigStore.get_names()) == 0
    utils.ConfigStore.set("foo", "bar")
    assert len(utils.ConfigStore.get_names()) == 1
    utils.ConfigStore.set("foo", "bar")
    assert len(utils.ConfigStore.get_names()) == 1
    utils.ConfigStore.set("foo1", "bar1")
    assert len(utils.ConfigStore.get_names()) == 2
    assert utils.ConfigStore.get("foo") == "bar"


def test_no_sqlite(capsys, mocker):
    mocker.patch("lumapps.api.utils._get_sqlite_ok", return_value=False)
    mocker.patch(
        "lumapps.api.utils._get_conn", return_value=utils._get_conn(":memory:")
    )
    c = utils._DiscoveryCacheSqlite
    assert c.get("foobar.com") is None
    c.set("foobar.com", "bla")
    assert c.get("foobar.com") == "bla"
    assert utils._DiscoveryCacheDict.get("foobar.com") == "bla"


def test_parse_endpoint_parts():
    s = ("user/get",)
    parts = utils._parse_endpoint_parts(s)
    assert parts == ["user", "get"]


def test_extract_from_discovery_spec():
    with open("tests/test_data/lumapps_discovery.json") as fh:
        discovery_doc = json.load(fh)
    name_parts = ["user", "get"]
    resources = discovery_doc["resources"]
    extracted = utils._extract_from_discovery_spec(resources, name_parts)

    assert extracted.get("httpMethod") == "GET"
    assert extracted.get("id") == "lumsites.user.get"


def test_pop_matches():
    d = {"a": 1, "b": {"c": 2, "d": {"e": 3}}, "z": 33}
    d2 = deepcopy(d)
    pth = "b/d/e"
    utils.pop_matches(pth, d2)
    assert d2 == {"a": 1, "b": {"c": 2, "d": {}}, "z": 33}
    d2 = deepcopy(d)
    pth = "b"
    utils.pop_matches(pth, d2)
    assert d2 == {"a": 1, "z": 33}
    d2 = deepcopy(d)
    pth = ""
    utils.pop_matches(pth, d2)
    assert d2 == d
    s = "not a dict"
    pth = "foo/bar"
    utils.pop_matches(pth, s)
    l1 = ["a", "b"]
    l2 = deepcopy(l1)
    utils.pop_matches(pth, l1)
    assert l2 == l1
    obj = "foo"
    utils.pop_matches("foo/bar", obj)
    assert obj == "foo"
