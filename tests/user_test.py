import unittest
import types
import mock

from apiclient.http import HttpMock
from apiclient.discovery import build

from lumapps.client import ApiClient
from lumapps.helpers.user import build_batch, get_by_email, list_users


class UserTests(unittest.TestCase):
    def setUp(self):
        credentials = mock.Mock(spec="google.oauth2.credentials.Credentials")
        email = "test@test.com"
        self.client = ApiClient(email, credentials=credentials)
        http = HttpMock("test_data/lumapps_discovery.json", {"status": "200"})
        service = build("lumapps", "v1", http=http, developerKey="no")
        self.client._service = service

    def test_build_batch(self):
        users = self.client.iter_call("user", "list")
        self.assertIsInstance(users, (list, types.GeneratorType))
        rep = build_batch(self.client, users)
        self.assertIsInstance(rep, types.GeneratorType)

    def test_get_by_email(self):
        # Test on itself
        get_by_email(self.client, self.client.email)

    def test_list_users(self):
        users = list_users(self.client)
        self.assertIsInstance(users, types.GeneratorType)
