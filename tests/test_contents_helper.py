from pytest import fixture

from lumapps.api.base_client import BaseClient
from lumapps.api.helpers.contents import list_contents_by_type

@fixture()
def cli():
    c = BaseClient(token="FAKE")
    return c


class MockResponse:
    def __init__(self, resp):
        self.resp = resp

    def json(self):
        return self.resp

def test_list_contents_by_type(mocker, cli: BaseClient):
    post_resp = {
        "lang": "en", 
        "customContentType": ["4697555889029120"]
    }

    def _prep_mocker():
        def mock_post(*args, **kwargs):
            return MockResponse(post_resp)

        mocker.patch("httpx.post", mock_post)
    
    _prep_mocker()
    data = open("tests/test_data/list_contents_by_type.json", "rb").read()
    assert data 