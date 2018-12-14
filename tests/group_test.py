import unittest
import types
import mock

from apiclient.http import HttpMock
from apiclient.discovery import build

from lumapps_api_client.lib import ApiClient
from lumapps_api_helpers.group import list as list_groups
from lumapps_api_helpers.group import build_batch


class GroupTests(unittest.TestCase):
    def setUp(self):
        credentials = mock.Mock(spec="google.oauth2.credentials.Credentials")
        email = "test@test.com"
        self.client = ApiClient(email, credentials=credentials)
        http = HttpMock("./test_data/lumapps_discovery.json", {"status": "200"})
        service = build("lumapps", "v1", http=http, developerKey="no")
        self.client._service = service

    def test_list_groups(self):
        with self.assertRaises(Exception):
            self.client.get_call("community", "list", body=None)
        with self.assertRaises(Exception):
            self.client.get_call("community", "list")

        groups = list_groups(self.client, body=None)
        self.assertIsInstance(groups, types.GeneratorType)

        groups = list_groups(self.client)
        self.assertIsInstance(groups, types.GeneratorType)

    def test_build_batch(self):
        groups = self.client.iter_call("feed", "search")
        batch = build_batch(self.client, groups)
        self.assertIsInstance(batch, types.GeneratorType)
