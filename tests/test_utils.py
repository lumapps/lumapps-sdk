from datetime import datetime, timedelta

from lumapps.api.utils import (
    list_prune_filters,
    _DiscoveryCacheDict,
    _DiscoveryCacheSqlite,
    DiscoveryCache,
    get_config_names,
    set_config,
    get_config,
    _get_conn,
    _parse_endpoint_parts,
)


def test_list_prune_filters(capsys):
    list_prune_filters()
    captured = capsys.readouterr()
    assert captured.out.startswith("PRUNE FILTERS:")


def test_discovery_cache_1():
    assert DiscoveryCache == _DiscoveryCacheSqlite


def test_discovery_cache_dict(mocker):
    mocker.patch("lumapps.api.utils.get_conf_db_file", return_value=":memory:")
    mocker.patch("lumapps.api.utils._get_conn", return_value=_get_conn())
    c = _DiscoveryCacheDict
    assert c.get("foobar.com") is None
    c.set("foobar.com", "bla")
    assert c.get("foobar.com") == "bla"
    c._cache["foobar.com"]["expiry"] = datetime.now() - timedelta(days=100)
    assert c.get("foobar.com") is None


def test_discovery_cache_sqlite(mocker):
    mocker.patch("lumapps.api.utils.get_conf_db_file", return_value=":memory:")
    mocker.patch("lumapps.api.utils._get_conn", return_value=_get_conn())
    c = _DiscoveryCacheSqlite
    assert c.get("foobar.com") is None
    c.set("foobar.com", "bla")
    assert c.get("foobar.com") == "bla"


def test_get_set_configs(mocker):
    mocker.patch("lumapps.api.utils.get_conf_db_file", return_value=":memory:")
    mocker.patch("lumapps.api.utils._get_conn", return_value=_get_conn())
    assert len(get_config_names()) == 0
    set_config("foo", "bar")
    assert len(get_config_names()) == 1
    set_config("foo", "bar")
    assert len(get_config_names()) == 1
    set_config("foo1", "bar1")
    assert len(get_config_names()) == 2
    assert get_config("foo") == "bar"


def test_parse_endpoint_parts():
    s = ("user/get",)
    parts = _parse_endpoint_parts(s)
    assert parts == ["user", "get"]
