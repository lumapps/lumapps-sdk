from json import load
import requests
from pytest import raises, fixture

from lumapps.api.client import ApiClient
from lumapps.api.errors import ApiClientError
from lumapps.api.helpers.medias import (
    _upload_new_media_file_of_given_lang,
    create_new_media,
    add_media_file_for_lang,
)


@fixture
def cli() -> ApiClient:
    c = ApiClient(token="foobar")
    with open("tests/test_data/lumapps_discovery.json") as fh:
        c._discovery_doc = load(fh)
    return c


class MockResponse:
    def __init__(self, resp):
        self.resp = resp

    def json(self):
        return self.resp


def test_upload_new_media_file_of_given_lang(mocker, cli: ApiClient):

    post_resp = {
        "blobKey": "fakeblobkey",
        "url": "https://fakeurl.com",
        "upload": "rien",
        "filelink": "rien",
    }

    def mock_get(*args, **kwargs):
        return MockResponse({"uploadUrl": "https://fake.com"})

    def mock_post(*args, **kwargs):
        return MockResponse(post_resp)

    mocker.patch("requests.get", mock_get)
    mocker.patch("requests.post", mock_post)

    with raises(ApiClientError):
        _upload_new_media_file_of_given_lang(
            cli, None, "fake", "fake", lang="en", prepare_for_lumapps=False
        )

    uploaded_file = _upload_new_media_file_of_given_lang(
        cli,
        "tests/test_data/content_1.json",
        "fake",
        "fake",
        lang="en",
        prepare_for_lumapps=False,
    )
    assert uploaded_file == post_resp

    uploaded_file = _upload_new_media_file_of_given_lang(
        cli,
        "tests/test_data/content_1.json",
        "fake",
        "fake",
        lang="en",
        prepare_for_lumapps=True,
    )
    assert "upload" not in uploaded_file
    assert uploaded_file["value"] == "fakeblobkey"


def test_create_new_media(mocker, cli: ApiClient):

    with raises(ApiClientError):
        create_new_media(cli, None, None, None, None, None)

    mocker.patch(
        "lumapps.api.client.ApiClient.get_call",
        return_value={"uploadUrl": "http://fake.com"},
    )
    # Test valid response
    post_resp = {"items": ["rien", "rien2"]}

    def mock_post(*args, **kwargs):
        return MockResponse(post_resp)

    mocker.patch("requests.post", mock_post)

    res = create_new_media(cli, b"rien", "fake", "filename", "png", True)
    assert res == "rien"

    post_resp = {"items": []}

    mocker.patch("requests.post", mock_post)
    res = create_new_media(cli, b"rien", "fake", "filename", "png", True)
    assert not res


def test_add_media_file_for_lang(mocker, cli: ApiClient):

    mocker.patch(
        "lumapps.api.helpers.medias._upload_new_media_file_of_given_lang",
        return_value=None,
    )
    res = add_media_file_for_lang(cli, "mediaTest", None, None, None)
    assert res == "mediaTest"

    mocker.patch(
        "lumapps.api.helpers.medias._upload_new_media_file_of_given_lang",
        return_value={"content": "rien"},
    )
    mocker.patch(
        "lumapps.api.client.ApiClient.get_call",
        return_value={"content": "rien"},
    )
    res = add_media_file_for_lang(cli, {"content": []}, None, None, None)
    assert res == {"content": "rien"}
