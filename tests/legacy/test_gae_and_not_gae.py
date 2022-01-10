from importlib import invalidate_caches, reload
from os import environ

import lumapps.api.utils


def test_gae():
    environ["GAE_ENV"] = "standard"
    try:
        reload(lumapps.api.utils)
        assert (
            type(lumapps.api.utils._discovery_cache)
            == lumapps.api.utils.DiscoveryCacheDict
        )
    finally:
        environ.pop("GAE_ENV", None)
        reload(lumapps.api.utils)
        invalidate_caches()
    assert (
        type(lumapps.api.utils._discovery_cache)
        == lumapps.api.utils.DiscoveryCacheSqlite
    )
