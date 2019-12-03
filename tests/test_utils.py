from datetime import datetime, timedelta

from mock import patch, MagicMock

from lumapps.api.utils import (
    list_prune_filters,
    _DiscoveryCacheDict,
    _DiscoveryCacheSqlite,
    DiscoveryCache,
    get_config_names,
    set_config,
    get_config,
    _unset_conn,
)


def test_list_prune_filters(capsys):
    list_prune_filters()
    captured = capsys.readouterr()
    assert captured.out.startswith("PRUNE FILTERS:")


def test_discovery_cache_1():
    assert DiscoveryCache == _DiscoveryCacheSqlite


def test_discovery_cache_dict():
    c = _DiscoveryCacheDict
    assert c.get('foobar.com') is None
    c.set('foobar.com', "bla")
    assert c.get('foobar.com') == "bla"
    c._cache['foobar.com']["expiry"] = datetime.now() - timedelta(days=100)
    assert c.get('foobar.com') is None


@patch("lumapps.api.utils.get_conf_db_file", MagicMock(return_value=":memory:"))
def test_discovery_cache_sqlite():
    _unset_conn()
    c = _DiscoveryCacheSqlite
    assert c.get('foobar.com') is None
    c.set('foobar.com', "bla")
    assert c.get('foobar.com') == "bla"


@patch("lumapps.api.utils.get_conf_db_file", MagicMock(return_value=":memory:"))
def test_get_set_configs():
    _unset_conn()
    assert len(get_config_names()) == 0
    set_config("foo", "bar")
    assert len(get_config_names()) == 1
    set_config("foo", "bar")
    assert len(get_config_names()) == 1
    set_config("foo1", "bar1")
    assert len(get_config_names()) == 2
    assert get_config("foo") == "bar"
