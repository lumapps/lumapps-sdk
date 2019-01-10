import unittest
import mock
import json

from apiclient.http import HttpMock
from apiclient.discovery import build

from lumapps_api_client.lib import ApiClient
from lumapps_api_helpers.media import uploaded_to_media


class TestMedia(unittest.TestCase):
    def setUp(self):
        credentials = mock.Mock(spec="google.oauth2.credentials.Credentials")
        self.client = ApiClient("test@test.com", credentials=credentials)
        http = HttpMock("test_data/lumapps_discovery.json", {"status": "200"})
        service = build("lumapps", "v1", http=http, developerKey="no")
        self.client._service = service

    def test_uploaded_to_media(self):
        # Test when name is given
        with open("test_data/uploaded_file.json", "r") as f:
            uploaded_file = json.load(f)
        lang = "en"
        instance = "20392"
        name = "test"
        media = uploaded_to_media(uploaded_file, instance, lang, name)
        assert media["content"][0]["value"] == uploaded_file["blobKey"]
        assert media["content"][0]["name"] == name
        assert media["content"][0]["lang"] == lang
        assert media["name"] == {lang: name}
        assert media["instance"] == instance

        # Test when name is not given
        media = uploaded_to_media(uploaded_file, instance, lang)
        assert media["content"][0]["value"] == uploaded_file["blobKey"]
        assert media["content"][0]["name"] == uploaded_file["name"]
        assert media["content"][0]["lang"] == lang
        assert media["name"] == {lang: uploaded_file["name"]}
        assert media["instance"] == instance

        # Test whith additionnal params
        key = "289830"
        media = uploaded_to_media(
            uploaded_file, instance, lang, hasCroppedContent=False, contentKey=key
        )
        assert media["hasCroppedContent"] is False
        assert media["contentKey"] == key
