import pytest


@pytest.fixture
def api_info() -> dict:
    return {"base_url": "https://go-cell-001.api.lumapps.com"}
