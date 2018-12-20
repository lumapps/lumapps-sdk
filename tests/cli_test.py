from copy import deepcopy
from lumapps_api_client.cli import load_config
import pytest


def test_load_config():
    with pytest.raises(SystemExit):
        api_info, auth_info, user = load_config(
            None, None, "ivo@managemybudget.net", "mmb"
        )
