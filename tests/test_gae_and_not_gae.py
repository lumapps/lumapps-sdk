from os import environ


def test_gae():
    environ['GAE_ENV'] = "standard"
    import lumapps.api.utils
    assert lumapps.api.utils.DiscoveryCache is lumapps.api.utils._DiscoveryCacheDict
