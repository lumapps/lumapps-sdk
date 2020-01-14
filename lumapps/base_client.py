import logging
import asyncio
import json

from urllib.parse import urljoin, urlparse
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
        api_spec: Union[
            str, dict
        ] = "https://lumsites.appspot.com/_ah/api/discovery/v1/apis/lumsites/v1/rest",
        run_async=False,
        session=None,
        no_verify=False,
        proxy_infos=None,
        timeout=30,
        headers: Optional[dict] = None,
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ):
        self.token = token
        self.base_url = base_url
        self.run_async = run_async
        self.session = session
        self.no_verify = no_verify
        self.proxy_infos = proxy_infos
        self.timeout = timeout
        self.headers = headers or {}
        self._logger = logging.getLogger(__name__)
        self._event_loop = loop if loop else self._get_event_loop()

        if isinstance(api_spec, str):
            if urlparse(api_spec).scheme != "":
                response = self.api_call(
                    api_spec, "GET", _format="json", force_sync=True
                )
                self.api_spec = response.data  # type: ignore
            else:
                with open(api_spec, "r") as f:
                    data = json.load(f)
                self.api_spec = data
        else:
            self.api_spec = api_spec

        if self.proxy_infos:
            self._proxy_host = proxy_infos["host"]
            self._proxy_port = proxy_infos["port"]
            self._proxy_url = f"{self._proxy_host}:{self._proxy_port}"
            self._proxy_headers = proxy_infos.get("headers")

            # Proxy authentication
            # Try to get it from the info, mus tbe an object (https://docs.aiohttp.org/en/stable/client_reference.html#client-session)
            self._proxy_auth = proxy_infos.get("proxy_auth")

            if (
                not self._proxy_auth
                and "user" in proxy_infos
                and "password" in proxy_infos
            ):
                # Construct a basic auth object from the proxy infos
                self._proxy_auth = aiohttp.BasicAuth(
                    login=proxy_infos["user"], password=proxy_infos["password"]
                )

    def _get_event_loop(self):
        """Retrieves the event loop or creates a new one."""
        try:
            return asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop

    def _get_headers(self, has_json):
        """Contructs the headers need for a request.
        Args:
            has_json (bool): Whether or not the request has json.
        Returns:
            The headers dictionary.
                e.g. {
                    'Content-Type': 'application/json;charset=utf-8',
                    'Authorization': 'Bearer xoxb-1234-1243',
                }
        """
        headers = {
            "Authorization": "Bearer {}".format(self.token),
            "Content-Type": "application/x-www-form-urlencoded;charset=utf-8",
        }
        if has_json:
            headers.update({"Content-Type": "application/json;charset=utf-8"})

        return headers

    def api_call(
        self,
        api_endpoint: str,
        http_verb: str = "POST",
        data: Union[dict, FormData] = None,
        params: dict = None,
        json: dict = None,
        _format: str = "json",
        full_url: bool = False,
        force_sync: bool = False,
    ) -> Union[asyncio.Future, LumAppsResponse]:
        """Create a request and execute the API call to LumApps.
        Args:
            api_endpoint (str): The target LumApps API endpoint.
                e.g. 'user/list'
            http_verb (str): HTTP Verb. e.g. 'POST'
            data: The body to attach to the request. If a dictionary is
                provided, form-encoding will take place.
                e.g. {'key1': 'value1', 'key2': 'value2'}
            params (dict): The URL parameters to append to the URL.
                e.g. {'key1': 'value1', 'key2': 'value2'}
            json (dict): JSON for the body to attach to the request
                (if files or data is not specified).
                e.g. {'key1': 'value1', 'key2': 'value2'}
            _format (str): The format of the response (json, text, bytes).
                Defaults to json.
        Returns:
            (LumAppsReponse)
                The server's response to an HTTP request. Data
                from the response can be accessed like a dict.
                If the response included 'cursor' it can
                be iterated on to execute subsequent requests.
        Raises:
            LumAppsApiCallError: The following LumApps API call failed:
                'user/getone'.
            LumAppsRequestError: Json data can only be submitted as
                POST requests.
        """
        has_json = json is not None
        if has_json and http_verb != "POST":
            msg = """Json data can only be submitted as POST requests.\
                    GET requests should use the 'params' argument."""
            raise err.LumAppsRequestError(msg)

        api_url = self._get_url(api_endpoint) if not full_url else api_endpoint

        req_args = {
            "headers": self._get_headers(has_json),
            "data": data,
            "params": params,
            "json": json,
        }

        if self._event_loop is None:
            self._event_loop = self._get_event_loop()

        future = asyncio.ensure_future(
            self._send(
                http_verb=http_verb,
                api_url=api_url,
                req_args=req_args,
                _format=_format,
            ),
            loop=self._event_loop,
        )

        if self.run_async and not force_sync:
            return future

        return self._event_loop.run_until_complete(future)

    def _get_url(self, api_endpoint):
        """Joins the base LumApps URL and an API method to form an absolute URL.
        Args:
            api_endpoint (str): The Slack Web API endpoint. e.g. 'user/list'
        Returns:
            The absolute API URL.
                e.g. 'https://lumsites.appspot.com/_ah/api/lumsites/v1/user/list'
        """
        return urljoin(self.base_url, api_endpoint)

    async def _request(self, *, http_verb, api_url, req_args, _format="json"):
        """Submit the HTTP request with the running session or a new session.
        Returns:
            A dictionary of the response data.
        """

        if self.proxy_infos:
            req_args["proxy"] = self._proxy_url
            if self._proxy_headers:
                req_args.update["proxy_headers"] = self._proxy_headers
            if self._proxy_auth:
                req_args["proxy_auth"] = self._proxy_auth

        if self.no_verify:
            req_args.update({"verify_ssl": False})

        async def format_res(res, _format="json"):
            if _format == "json":
                return {
                    "data": await res.json(),
                    "headers": res.headers,
                    "status_code": res.status,
                }
            elif _format == "binary":
                return {
                    "data": await res.read(),
                    "headers": res.headers,
                    "status_code": res.status,
                }
            else:
                return {
                    "data": await res.text(),
                    "headers": res.headers,
                    "status_code": res.status,
                }

        if self.session and not self.session.closed:
            async with self.session.request(
                http_verb, api_url, **req_args
            ) as res:
                return await format_res(res, _format)
        async with aiohttp.ClientSession(
            loop=self._event_loop,
            timeout=aiohttp.ClientTimeout(total=self.timeout),
        ) as session:
            async with session.request(http_verb, api_url, **req_args) as res:
                return await format_res(res, _format)

    async def _send(self, http_verb, api_url, req_args, _format="json"):
        res = await self._request(
            http_verb=http_verb,
            api_url=api_url,
            req_args=req_args,
            _format=_format,
        )

        data = {
            "client": self,
            "http_verb": http_verb,
            "api_url": api_url,
            "req_args": req_args,
        }
        return LumAppsResponse(**{**data, **res}).validate()
