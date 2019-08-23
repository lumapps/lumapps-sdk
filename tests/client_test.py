# Standard Imports
import unittest
import asyncio
import types

from typing import Generator

import lumapps
from lumapps.errors import LumAppsClientError, LumAppsApiError

from tests.helpers import (
    async_test,
    add_list_data_to_mock,
    mock_request,
    add_user_to_mock,
    add_list_communities_data_to_mock,
)


@unittest.mock.patch(
    "lumapps.LumAppsApiClient._request", new_callable=mock_request
)
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


class TestGetCall(unittest.TestCase):
    def setUp(self):
        self.client = lumapps.LumAppsApiClient(
            "token-bidon", loop=asyncio.get_event_loop()
        )

    def test_get_call_raise_error_for_non_known_endpoint(self):
        with self.assertRaises(LumAppsClientError):
            self.client.get_call("user", "getter")

    def test_get_call_with_no_creds_raise_error(self):
        with self.assertRaises(LumAppsApiError):
            self.client.get_call("user", "get")

    @unittest.mock.patch(
        "lumapps.LumAppsApiClient._request", new_callable=mock_request
    )
    def test_get_call_with_args(self, mock_request):
        test_email = "maxime@test.lumapps.com"
        add_user_to_mock(mock_request, test_email)
        res = self.client.get_call("user", "get", email=test_email)[0]
        self.assertEqual(res.get("email"), test_email)

    @unittest.mock.patch(
        "lumapps.LumAppsApiClient._request", new_callable=mock_request
    )
    def test_get_call_with_args_and_body(self, mock_request):
        add_list_communities_data_to_mock(mock_request)
        res = self.client.get_call(
            "community", "list", fields="items(id)", body={"lang": "fr"}
        )
        self.assertIsInstance(res, list)
        self.assertEqual(len(res), 4)


class TestIterCall(unittest.TestCase):
    def setUp(self):
        self.client = lumapps.LumAppsApiClient(
            "token-bidon", loop=asyncio.get_event_loop()
        )

    def test_iter_call_raise_error_for_non_known_endpoint(self):
        with self.assertRaises(LumAppsClientError):
            list(self.client.iter_call("user", "getter"))

    def test_get_iter_with_no_creds_raise_error(self):
        with self.assertRaises(LumAppsApiError):
            list(self.client.iter_call("user", "get"))

    @unittest.mock.patch(
        "lumapps.LumAppsApiClient._request", new_callable=mock_request
    )
    def test_iter_call_with_args(self, mock_request):
        test_email = "maxime@test.lumapps.com"
        add_user_to_mock(mock_request, test_email)
        res = list(self.client.iter_call("user", "get", email=test_email))
        self.assertEqual(res[0].get("email"), test_email)

    @unittest.mock.patch(
        "lumapps.LumAppsApiClient._request", new_callable=mock_request
    )
    def test_get_call_with_args_and_body(self, mock_request):
        add_list_communities_data_to_mock(mock_request)
        res = self.client.iter_call(
            "community", "list", fields="items(id)", body={"lang": "fr"}
        )
        self.assertIsInstance(res, Generator)
        self.assertEqual(len(list(res)), 4)


class TestLumAppsApiCientStaticMethods(unittest.TestCase):
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
