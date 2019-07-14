import logging
import asyncio
from urllib.parse import urljoin
from typing import Optional, Union

import aiohttp
from aiohttp import FormData

from lumapps.lumapps_reponse import LumAppsResponse
import lumapps.errors as err


class LumAppsBaseClient:
    BASE_URL = "https://lumsites.appspot.com/_ah/api/lumsites/v1/"

    def __init__(
        self,
        token=None,
        base_url=BASE_URL,
        run_async=False,
        session=None,
        proxy=None,
        timeout=30,
        headers: Optional[dict] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ):
        self.token = token
        self.base_url = base_url
        self.run_async = run_async
        self.session = session
        self.proxy = proxy
        self.timeout = timeout
        self.headers = headers or {}
        self._logger = logging.getLogger(__name__)
        self._event_loop = loop

    def authenticate(self, token):
        pass

    def _get_event_loop(self):
        """Retrieves the event loop or creates a new one."""
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

    def _get_headers(self, has_json, has_files):
        """Contructs the headers need for a request.
        Args:
            has_json (bool): Whether or not the request has json.
        Returns:
            The headers dictionary.
                e.g. {
                    'Content-Type': 'application/json;charset=utf-8',
                    'Authorization': 'Bearer xoxb-1234-1243',
                    'User-Agent': 'Python/3.6.8 slack/2.1.0 Darwin/17.7.0'
                }
        """
        headers = {
            "Authorization": "Bearer {}".format(self.token),
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        }
        if has_json:
            headers.update({"Content-Type": "application/json;charset=utf-8"})

        if has_files:
            # These are set automatically by the aiohttp library.
            headers.pop("Content-Type", None)

        return headers

    def api_call(
        self,
        api_endpoint: str,
        http_verb: str = "POST",
        files: dict = None,
        data: Union[dict, FormData] = None,
        params: dict = None,
        json: dict = None,
    ) -> Union[asyncio.Future, LumAppsResponse]:
        """Create a request and execute the API call to LumApps.
        Args:
            api_endpoint (str): The target LumApps API endpoint.
                e.g. 'user/list'
            http_verb (str): HTTP Verb. e.g. 'POST'
            files (dict): Files to multipart upload.
                e.g. {imageORfile: file_objectORfile_path}
            data: The body to attach to the request. If a dictionary is
                provided, form-encoding will take place.
                e.g. {'key1': 'value1', 'key2': 'value2'}
            params (dict): The URL parameters to append to the URL.
                e.g. {'key1': 'value1', 'key2': 'value2'}
            json (dict): JSON for the body to attach to the request
                (if files or data is not specified).
                e.g. {'key1': 'value1', 'key2': 'value2'}
        Returns:
            (LumAppsReponse)
                The server's response to an HTTP request. Data
                from the response can be accessed like a dict.
                If the response included 'cursor' it can
                be iterated on to execute subsequent requests.
        Raises:
            LumAppsApiCallError: The following LumApps API call failed:
                'chat.postMessage'.
            LumAppsRequestError: Json data can only be submitted as
                POST requests.
        """
        has_json = json is not None
        has_files = files is not None
        if has_json and http_verb != "POST":
            msg = "Json data can only be submitted as POST requests. GET requests should use the 'params' argument."
            raise err.LumAppsRequestError(msg)

        api_url = self._get_url(api_endpoint)

        req_args = {"headers": self._get_headers(has_json, has_files)}

        if self._event_loop is None:
            self._event_loop = self._get_event_loop()

        future = asyncio.ensure_future(
            self._send(http_verb=http_verb, api_url=api_url, req_args=req_args),
            loop=self._event_loop,
        )

        if self.run_async:
            return future

        return self._event_loop.run_until_complete(future)

    def _get_url(self, api_endpoint):
        """Joins the base LumApps URL and an API method to form an absolute URL.
        Args:
            api_endpoint (str): The Slack Web API endpoint. e.g. 'user/list'
        Returns:
            The absolute API URL.
                e.g. 'https://lumsites.appspot.com/_ah/apu/lumsites/v1/user/list'
        """
        return urljoin(self.base_url, api_endpoint)

    async def _request(self, *, http_verb, api_url, req_args):
        """Submit the HTTP request with the running session or a new session.
        Returns:
            A dictionary of the response data.
        """
        if self.session and not self.session.closed:
            async with self.session.request(http_verb, api_url, **req_args) as res:
                return {
                    "data": await res.json(),
                    "headers": res.headers,
                    "status_code": res.status,
                }
        async with aiohttp.ClientSession(
            loop=self._event_loop, timeout=aiohttp.ClientTimeout(total=self.timeout)
        ) as session:
            async with session.request(http_verb, api_url, **req_args) as res:
                return {
                    "data": await res.json(),
                    "headers": res.headers,
                    "status_code": res.status,
                }

    async def _send(self, http_verb, api_url, req_args):
        res = await self._request(
            http_verb=http_verb, api_url=api_url, req_args=req_args
        )
        data = {
            "client": self,
            "http_verb": http_verb,
            "api_url": api_url,
            "req_args": req_args,
        }
        return LumAppsResponse(**{**data, **res}).validate()
