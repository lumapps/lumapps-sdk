import json
import logging

from lumapps_api_client.lib import ApiClient
from pathlib2 import Path

AUTH_INFO_FILE = 'test_data/local_auth.json'
SERVICE_AUTH_FILE = 'test_data/service_auth.json'


def setup_logger():
    level = logging.DEBUG
    logger = logging.getLogger()
    logger.setLevel(level)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s')
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)


def test_get_bearer_token():
    with Path(AUTH_INFO_FILE).open() as fh:
        auth_info = json.load(fh)
    api_client = ApiClient(auth_info)
    assert api_client.bearer_token is not None


def test_reuse_api():
    setup_logger()
    with Path(SERVICE_AUTH_FILE).open() as fh:
        auth_info = json.load(fh)
    api_token = ApiClient(
        auth_info,
        user='lvaugeois@managemybudget.net'
    )
    token_ludo = api_token.get_call(
        'user', 'getToken',
        customerId='5678444713082880',
        email='lvaugeois@managemybudget.net'
    )["accessToken"]
    token_ivo = api_token.get_call(
        'user', 'getToken',
        customerId='5678444713082880',
        email='ivo@managemybudget.net'
    )["accessToken"]
    api = ApiClient()
    api.token = token_ludo
    assert api.get_call('user', 'get')['email'] == 'lvaugeois@managemybudget.net'
    api.token = token_ivo
    assert api.get_call('user', 'get')['email'] == 'ivo@managemybudget.net'
