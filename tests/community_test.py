import unittest
import mock
import types

from apiclient.http import HttpMock
from apiclient.discovery import build

from lumapps.client.lib import ApiClient
from lumapps.helpers.community import build_batch, list_communities


class CommunitiesTest(unittest.TestCase):
    def setUp(self):
        credentials = mock.Mock(spec="google.oauth2.credentials.Credentials")
        self.client = ApiClient("test@test.com", credentials=credentials)
        http = HttpMock("test_data/lumapps_discovery.json", {"status": "200"})
        service = build("lumapps", "v1", http=http, developerKey="no")
        self.client._service = service

    def test_list_communities(self):
        rep = list_communities(self.client)
        self.assertIsInstance(rep, types.GeneratorType)

    def test_build_batch(self):
        communities = list_communities(self.client)
        batch = build_batch(self.client, communities)
        self.assertIsInstance(batch, types.GeneratorType)
