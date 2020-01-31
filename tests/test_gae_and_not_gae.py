from os import environ
from importlib import reload

import lumapps.api.utils


def test_gae():
    environ['GAE_ENV'] = "standard"
    reload(lumapps.api.utils)
    assert lumapps.api.utils.DiscoveryCache is lumapps.api.utils._DiscoveryCacheDict
