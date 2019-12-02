from datetime import datetime, timedelta

from mock import patch, MagicMock

from lumapps.api.utils import (
    list_prune_filters,
    _DiscoveryCacheDict,
    _DiscoveryCacheSqlite,
    DiscoveryCache,
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
    c = _DiscoveryCacheSqlite
    assert c.get('foobar.com') is None
    c.set('foobar.com', "bla")
    assert c.get('foobar.com') == "bla"
