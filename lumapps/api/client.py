from __future__ import print_function, unicode_literals
import json
from time import time
from textwrap import TextWrapper

import uritemplate
import httplib2
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials
from googleapiclient.errors import HttpError
from googleapiclient.discovery import (
    build_from_document,
    DISCOVERY_URI,
    V2_DISCOVERY_URI,
    _retrieve_discovery_doc,
)

from lumapps.api.utils import (
    DiscoveryCache,
    pop_matches,
    ApiCallError,
    GOOGLE_APIS,
    FILTERS,
)


def _get_build_content(
    serviceName,
    version,
    discoveryServiceUrl=DISCOVERY_URI,
    cache_discovery=True,
    cache=None,
    proxy_info=None,
):
    params = {"api": serviceName, "apiVersion": version}
    discovery_http = httplib2.Http(timeout=60)
    if proxy_info:
        discovery_http.proxy_info = httplib2.ProxyInfo(
            httplib2.socks.PROXY_TYPE_HTTP_NO_TUNNEL,
            proxy_info["host"],
            proxy_info["port"],
            proxy_user=proxy_info["user"],
            proxy_pass=proxy_info["password"],
        )
    discovery_http.disable_ssl_certificate_validation = True
    for discovery_url in (discoveryServiceUrl, V2_DISCOVERY_URI):
        requested_url = uritemplate.expand(discovery_url, params)
        try:
            return _retrieve_discovery_doc(
                requested_url, discovery_http, cache_discovery, cache
            )
        except HttpError as e:
            if e.resp.status == 404:
                continue
            else:
                raise e
    raise Exception("name: %s  version: %s" % (serviceName, version))


def _parse_method_parts(parts):
    ret = []
    for part in parts:
        for sub_part in part.split("/"):
            ret.append(sub_part)
    return ret


class ApiClient(object):
    """
        Args:
            user (str): The user email.
            auth_info (dict): A service account key (json file).
            api_info (dict): A dict containing the description of your api. If
                no api_info is given this defaults to the lumsites api infos.
            credentials (dict): oauth2 credentials.
            token (str): A bearer token.
            token_getter (object): a token getter function
            prune (bool): Whether or not to use FILTERS to prune the LumApps
                API responses. Defaults to False.
            num_retries (int): Number of times that a request will be retried.
                Default to 1.

        Note:
            At least one type of authentication info is required (auth_info,
            credentials, token)
    """

    def __init__(
        self,
        auth_info=None,
        api_info=None,
        credentials=None,
        user=None,
        token=None,
        token_getter=None,
        prune=False,
        num_retries=1,
        no_verify=False,
        proxy_info=None,
    ):
        self._get_token_user = None
        self._token_expiry = 0
        self.num_retries = num_retries
        self.no_verify = no_verify
        self.proxy_info = proxy_info
        self.prune = prune
        self._auth_info = auth_info
        self._user = {}
        self.last_cursor = None
        self.token_expiration = None

        # Api infos setup : construct the api url.
        if not api_info:
            api_info = {}
        self.api_info = api_info
        self._api_name = api_info.get("name", "lumsites")
        self._api_scopes = api_info.get(
            "scopes", ["https://www.googleapis.com/auth/userinfo.email"]
        )
        self._api_version = api_info.get("version", "v1")
        self.base_url = api_info.get("base_url", "https://lumsites.appspot.com").rstrip(
            "/"
        )
        if self._api_name in GOOGLE_APIS:
            url_path = "discovery/v1/apis"
        else:
            url_path = "_ah/api/discovery/v1/apis"
        self._url = "{}/{}/{}/{}/rest".format(
            self.base_url, url_path, self._api_name, self._api_version
        )
        self._methods = None
        self._service = None
        self.token_getter = token_getter
        if token_getter:
            self.creds = None
            self._check_access_token()
        elif credentials:
            self.creds = credentials
        elif auth_info and "refresh_token" in auth_info:
            self.creds = Credentials(None, **auth_info)
        elif auth_info and "bearer" in auth_info:
            self.creds = Credentials(auth_info["bearer"].replace("Bearer ", ""))
        elif token:
            self.creds = None
            self.token = token
        elif auth_info:  # service account
            self.creds = service_account.Credentials.from_service_account_info(
                auth_info
            )
            if self._api_scopes:
                self.creds = self.creds.with_scopes(self._api_scopes)
            if user:
                self.creds = self.creds.with_subject(user)
        else:
            raise Exception(
                "You must provide authentication infos (token_getter, "
                "auth_info, credentials or token)."
            )
        self.email = user or ""

    def _check_access_token(self):
        if not self.token_getter:
            return
        exp = self._token_expiry
        if exp and exp > time() + 120:
            return
        self.token, self._token_expiry = self.token_getter()

    def _prune(self, method_parts, content):
        """Prune the api response.
        """
        if not self.prune:
            return content
        for filter_method in FILTERS:
            filter_method_parts = filter_method.split("/")
            if len(method_parts) != len(filter_method_parts):
                continue
            for filter_part, part in zip(filter_method_parts, method_parts):
                if filter_part not in ("*", part):
                    break
            else:
                for pth in FILTERS[filter_method]:
                    if isinstance(content, list):
                        for o in content:
                            pop_matches(pth, o)
                    else:
                        pop_matches(pth, content)
        return content

    def get_new_client_as(self, user):
        return ApiClient(self._auth_info, self.api_info, user=user)

    @property
    def token(self):
        if not self.creds.token:
            self.service._http.request(self.base_url)
        return self.creds.token

    @token.setter
    def token(self, v):
        if self.creds and self.creds.token == v:
            return
        self._service = None
        self.creds = Credentials(v)

    @property
    def service(self):
        """Setup the service object.
        """
        self._check_access_token()
        if self._service is None:
            build_content = _get_build_content(
                self._api_name,
                self._api_version,
                discoveryServiceUrl=self._url,
                cache_discovery=True,
                cache=DiscoveryCache(),
                proxy_info=self.proxy_info,
            )
            self._service = build_from_document(build_content, credentials=self.creds)
            if self.no_verify:
                self._service._http.http.disable_ssl_certificate_validation = True
            if self.proxy_info:
                self._service._http.http.proxy_info = httplib2.ProxyInfo(
                    httplib2.socks.PROXY_TYPE_HTTP_NO_TUNNEL,
                    self.proxy_info["host"],
                    self.proxy_info["port"],
                    proxy_user=self.proxy_info["user"],
                    proxy_pass=self.proxy_info["password"],
                )
        return self._service

    @property
    def methods(self):
        if self._methods is None:
            self._methods = {
                n: m for n, m in self.walk_api_methods(self.service._resourceDesc)
            }
        return self._methods

    def get_help(self, method_parts, debug=False):
        help_lines = []

        def w(l):
            help_lines.append(l)

        wrapper = TextWrapper(initial_indent="\t", subsequent_indent="\t")
        method = self.methods[method_parts]
        w(method.get("httpMethod", "?") + " method: " + " ".join(method_parts) + "\n")
        if "description" in method:
            w(method["description"].strip() + "\n")
        if debug:
            w(json.dumps(method, indent=4, sort_keys=True))
        params = method.get("parameters", {})
        if method.get("httpMethod", "") == "POST":
            params.update(
                {"body": {"required": True, "type": "JSON"}, "fields": {"type": "JSON"}}
            )
        if not params:
            w("API method takes no parameters")
        else:
            w("Parameters (*required):")
            for param_name in sorted(params):
                param = params[param_name]
                descr = param.get("description")
                descr = "\n" + wrapper.fill(descr) if descr else ""
                w(
                    "  {}: {} {} {}".format(
                        param_name,
                        param["type"],
                        "*" if param.get("required") else "",
                        descr,
                    )
                )
        return "\n".join(help_lines)

    def get_method_descriptions(self, methods):
        lines = []
        for method_parts in methods:
            method = self.methods[method_parts]
            lines.append(
                (
                    " ".join(method_parts),
                    method.get("description", "").strip().split("\n")[0],
                )
            )
        longest_name = max(len(l[0]) for l in lines)
        fmt = "  {{: <{}}}  {{}}".format(longest_name)
        return "\n".join(fmt.format(*l) for l in lines)

    def walk_api_methods(self, resource, parents=()):
        for method_name, method in resource.get("methods", {}).items():
            yield tuple(parents + (method_name,)), method
        for rsc_name, rsc in resource.get("resources", {}).items():
            for method_name, method in self.walk_api_methods(
                rsc, tuple(parents + (rsc_name,))
            ):
                yield method_name, method

    def _get_api_call(self, method_parts, params):
        """Construct the method to call by using the service.
        """
        api_call = self.service
        for part in method_parts[:-1]:
            api_call = getattr(api_call, part)()
        try:
            return getattr(api_call, method_parts[-1])(**params)
        except TypeError as err:
            raise ApiCallError(err)

    def get_call(self, *method_parts, **params):
        """
        Args:
            *method_parts (str): API method.
            **params: Parameters.

        Returns:
            dict: An object, or list of objects returned by API method.

        Example:
            List feedtypes in LumApps:
            -> GET https://.../_ah/api/lumsites/v1/feedtype/list

            With this method:

                >>> feedtypes = get_call("feedtype", "list")
                >>> print(feedtypes)
        """
        if params is None:
            params = {}
        method_parts = _parse_method_parts(method_parts)
        items = []
        cursor = None
        if "body" in params and isinstance(params["body"], str):
            params["body"] = json.loads(params["body"])
        while True:
            if cursor:
                if "body" in params:
                    params["body"]["cursor"] = cursor
                else:
                    params["cursor"] = cursor
            response = self._get_api_call(method_parts, params).execute(
                num_retries=self.num_retries
            )
            if "more" in response and "items" not in response:
                self.last_cursor = None
                return items  # empty list
            if "more" in response and "items" in response:
                items.extend(response["items"])
                if response.get("more", False):
                    self.last_cursor = cursor = response["cursor"]
                else:
                    return self._prune(method_parts, items)
            else:
                self.last_cursor = None
                return self._prune(method_parts, response)

    def iter_call(self, *method_parts, **params):
        """
        Args:
            *method_parts (str): API method.
            **params: Parameters.

        Yields:
            dict: Objects returned by API method.

        Example:
            List feedtypes in LumApps:
            -> GET https://.../_ah/api/lumsites/v1/feedtype/list

            With this method:

                >>> feedtypes = iter_call("feedtype", "list")
                >>> for feedtype in feedtypes: print(feedtype)
        """
        if params is None:
            params = {}
        method_parts = _parse_method_parts(method_parts)
        cursor = None
        if "body" in params and isinstance(params["body"], str):
            params["body"] = json.loads(params["body"])
        while True:
            if cursor:
                if "body" in params:
                    params["body"]["cursor"] = cursor
                else:
                    params["cursor"] = cursor
            response = self._get_api_call(method_parts, params).execute(
                num_retries=self.num_retries
            )
            if "more" in response and "items" not in response:
                return  # empty list
            if "more" in response and "items" in response:
                for item in response["items"]:
                    yield self._prune(method_parts, item)
                if response.get("more", False):
                    cursor = response["cursor"]
                else:
                    return
            else:
                yield self._prune(method_parts, response)

    def get_matching_methods(self, method_parts):
        # find exact matches of all parts up to but excluding last
        matches = [n for n in self.methods if len(n) >= len(method_parts)]
        for i, part in enumerate(method_parts[:-1]):
            matches = [n for n in matches if len(n) >= i and n[i] == part]
        # find 'startswith' matches of the last part
        last = method_parts[-1]
        idx = len(method_parts) - 1
        matches = [m for m in matches if len(m) >= idx and m[idx].startswith(last)]
        if not matches:
            return "API method not found"
        return (
            "API method not found. Did you mean any of these?\n"
            + self.get_method_descriptions(sorted(matches))
        )
