# Standard Imports
import unittest
from unittest import mock
import asyncio
import types

import lumapps
from tests.helpers import async_test, add_list_data_to_mock, mock_request
from lumapps.errors import LumAppsClientError


@mock.patch("lumapps.LumAppsApiClient._request", new_callable=mock_request)
class TestLumAppsApiCient(unittest.TestCase):
    def setUp(self):
        self.client = lumapps.LumAppsApiClient(
            "token-xoxb-abc-123", loop=asyncio.get_event_loop()
        )

    def tearDown(self):
        pass

    @async_test
    async def test_api_calls_return_a_future_when_run_in_async_mode(
        self, mock_request
    ):
        self.client.run_async = True
        future = self.client.api_call("user/list")
        self.assertTrue(asyncio.isfuture(future))
        resp = await future
        self.assertTrue(resp["test"])

    def test_list_all(self, mock_request):
        add_list_data_to_mock(mock_request)
        users = self.client.list_all("user/list")
        self.assertTrue(len(users) == 4)

    def test_iter_pages(self, mock_request):
        add_list_data_to_mock(mock_request)
        pages = self.client.iter_pages("user/list")
        self.assertIsInstance(pages, types.GeneratorType)
        self.assertTrue(len(list(pages)) == 2)

    def test_iter_entities(self, mock_request):
        add_list_data_to_mock(mock_request)
        pages = self.client.iter_entities("user/list")
        self.assertIsInstance(pages, types.GeneratorType)
        self.assertTrue(len(list(pages)) == 4)

    def test_get_call_raise_error_for_non_known_endpoint(self, mock_request):
        client = lumapps.LumAppsApiClient()

        with self.assertRaises(LumAppsClientError):
            client.get_call("user", "getter")


class TestLumAppsApiCientStatixMethods(unittest.TestCase):
    def setUp(self):
        self.client = lumapps.LumAppsApiClient(
            "token-xoxb-abc-123", loop=asyncio.get_event_loop()
        )

    def test_parse_list_endpoint(self):

        # Test left unchanged
        endpoint = "user/list"
        parsed_endpoint = self.client._parse_list_endpoint(endpoint)
        self.assertTrue(parsed_endpoint == "user/list")

        # Test put it in the right format
        endpoint = "user"
        parsed_endpoint = self.client._parse_list_endpoint(endpoint)
        self.assertTrue(parsed_endpoint == "user/list")

        endpoint = "feed"
        parsed_endpoint = self.client._parse_list_endpoint(endpoint)
        self.assertTrue(parsed_endpoint == "feed/list")

    def test_extract_method_from_discovery(self):
        client = lumapps.LumAppsApiClient()
        r1 = client._extract_method_from_discovery("user", "save")
        r2 = client._extract_method_from_discovery("user", "directory", "list")
        r3 = client._extract_method_from_discovery("user", "getToken")
        r4 = client._extract_method_from_discovery("user", "not")

        self.assertTrue(r1 and r2 and r3 and not r4)

        verbs = [
            r1.get("httpMethod"),
            r2.get("httpMethod"),
            r3.get("httpMethod"),
            r4.get("httpMethod"),
        ]
        self.assertEqual(verbs, ["POST", "GET", "GET", None])
