from json import loads, dumps
from time import time
from textwrap import TextWrapper
from typing import Any, Dict, Optional

from requests import Session
from authlib.integrations.requests_client import OAuth2Session, AssertionSession

# from authlib.integrations.httpx_client import OAuth2Client, AssertionClient

from lumapps.api.errors import ApiClientError, ApiCallError
from lumapps.api.utils import (
    DiscoveryCache,
    pop_matches,
    GOOGLE_APIS,
    FILTERS,
    _parse_endpoint_parts,
    _extract_from_discovery_spec,
)


class ApiClient(object):
    """
        Args:
            user (str): The user email.
            auth_info (dict): A session account key (json file).
            api_info (dict): A dict containing the description of your api. If
                no api_info is given this defaults to the lumsites api infos.
            credentials (dict): oauth2 credentials.
            token (str): A bearer token.
            token_getter (object): a token getter function
            prune (bool): Whether or not to use FILTERS to prune the LumApps
                API responses. Defaults to False.
            no_verify (bool): Wether or not to verify ssl connexion. Defaults to False
            proxy_info (dict): Necessary infos for a connexion via a proxy. Defaults to None.

        Notes:
            At least one type of authentication info is required (auth_info,
            credentials, token)
    """

    def __init__(
        self,
        auth_info: Optional[Dict[str, Any]] = None,
        api_info: Optional[Dict[str, Any]] = None,
        user: Optional[str] = None,
        token: Optional[str] = None,
        token_getter: Optional[Any] = None,
        prune: bool = False,
        no_verify: bool = False,
        proxy_info: Optional[Dict[str, Any]] = None,
    ):
        self._get_token_user = None
        self._token_expiry = 0
        self.no_verify = no_verify
        self.proxy_info = proxy_info
        self.prune = prune
        self._auth_info = auth_info
        self._user = {}
        self._token = None
        self._endpoints = None
        self._session = None
        self._headers = {}
        self.token_expiration = None
        if not api_info:
            api_info = {}
        self.api_info = api_info
        self._api_name = api_info.get("name", "lumsites")
        scope = api_info.get(
            "scopes", ["https://www.googleapis.com/auth/userinfo.email"]
        )
        self._scope = " ".join(scope)
        self._api_version = api_info.get("version", "v1")
        self.base_url = api_info.get("base_url", "https://lumsites.appspot.com").rstrip(
            "/"
        )
        if self._api_name in GOOGLE_APIS:
            prefix = f"{self.base_url}"
        else:
            prefix = f"{self.base_url}/_ah/api"
        api_name, api_version = self._api_name, self._api_version
        self._api_url = f"{prefix}/{api_name}/{api_version}"
        self._discovery_url = (
            f"{prefix}/discovery/v1/apis/{api_name}/{api_version}/rest"
        )
        self.token_getter = token_getter
        self.email = user or ""
        self._discovery_doc = None
        self.token = token

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, v):
        if self._token and self._token == v:
            return
        self._token = v
        self._headers["authorization"] = f"Bearer {self._token}"
        if self._session:
            self._session.headers.update(self._headers)

    def _create_session(self):
        auth = self._auth_info
        if not auth and self._token:
            s = Session()
        elif auth and "refresh_token" in auth:
            s = OAuth2Session(
                client_id=auth["client_id"],
                client_secret=auth["client_secret"],
                scope=self._scope,
            )
            s.refresh_token(auth["token_uri"], refresh_token=auth["refresh_token"])
        elif auth:  # service account
            claims = {"scope": self._scope} if self._scope else {}
            s = AssertionSession(
                token_endpoint=auth["token_uri"],
                issuer=auth["client_email"],
                audience=auth["token_uri"],
                claims=claims,
                subject=self.email or None,
                key=auth["private_key"],
                header={"alg": "RS256"},
            )
        else:
            raise ApiClientError(
                "You must provide authentication infos (token_getter, "
                "auth_info, credentials or token)."
            )
        s.verify = not self.no_verify
        if self.proxy_info:
            scheme = self.proxy_info.get("scheme", "https")
            host = self.proxy_info["host"]
            port = self.proxy_info["port"]
            user = self.proxy_info["user"]
            pwd = self.proxy_info["password"]
            s.proxies.update({"https": f"{scheme}://{user}:{pwd}@{host}:{port}"})
            s.proxies.update({"http": f"{scheme}://{user}:{pwd}@{host}:{port}"})
        s.headers.update(self._headers)
        return s

    @property
    def session(self):
        """Setup the session object."""
        self._check_access_token()
        if self._session is None:
            self._session = self._create_session()
        return self._session

    @property
    def discovery_doc(self):
        if self._discovery_doc is None:
            url = self._discovery_url
            d = DiscoveryCache.get(url)
            if d:
                self._discovery_doc = loads(d)
            else:
                resp = self.session.get(url)
                DiscoveryCache.set(url, resp.text)
                self._discovery_doc = resp.json()
        return self._discovery_doc

    def _check_access_token(self):
        if not self.token_getter:
            return
        exp = self._token_expiry
        if exp and exp > time() + 120:
            return
        self.token, self._token_expiry = self.token_getter()

    def _prune(self, name_parts, content):
        """Prune the api response.
        """
        if not self.prune:
            return content
        for ep_filter in FILTERS:
            ep_filter_parts = ep_filter.split("/")
            if len(name_parts) != len(ep_filter_parts):
                continue
            for filter_part, part in zip(ep_filter_parts, name_parts):
                if filter_part not in ("*", part):
                    break
            else:
                for pth in FILTERS[ep_filter]:
                    if isinstance(content, list):
                        for o in content:
                            pop_matches(pth, o)
                    else:
                        pop_matches(pth, content)
        return content

    def get_new_client_as_using_dwd(self, user_email: str) -> "ApiClient":
        """ Get a new ApiClient using domain-wide delegation """
        return ApiClient(
            auth_info=self._auth_info,
            api_info=self.api_info,
            user=user_email,
            no_verify=self.no_verify,
            proxy_info=self.proxy_info,
            prune=self.prune,
        )

    def get_new_client_as(
        self, user_email: str, customer_id: Optional[str] = None
    ) -> "ApiClient":
        """ Get a new ApiClient using an authorized session account by obtaining a
            token using the user/getToken endpoint.

            Args:
                user_email (str): User you want to authenticate on behalf of
                customer_id (str): Id of the LumApps customer the user belong to

            Returns:
                ApiClient: A new instance of the ApiClient correctly authenticated.
        """
        if not self.creds:
            raise ApiClientError("No credentials (auth_info) provided")
        token_infos = self.get_call(
            "user/getToken", customerId=customer_id, email=user_email
        )
        token = token_infos["accessToken"]
        return ApiClient(
            api_info=self.api_info,
            token=token,
            user=user_email,
            no_verify=self.no_verify,
            proxy_info=self.proxy_info,
            prune=self.prune,
        )

    @property
    def endpoints(self):
        if self._endpoints is None:
            self._endpoints = {n: m for n, m in self.walk_endpoints(self.discovery_doc)}
        return self._endpoints

    def get_help(self, name_parts, debug=False):
        help_lines = []

        def add_line(l):
            help_lines.append(l)

        wrapper = TextWrapper(initial_indent="\t", subsequent_indent="\t")
        ep_info = self.endpoints[name_parts]
        method = ep_info.get("httpMethod", "?")
        add_line(f"{method} endpoint: " + " ".join(name_parts) + "\n")
        if "description" in ep_info:
            add_line(ep_info["description"].strip() + "\n")
        if debug:
            add_line(dumps(ep_info, indent=4, sort_keys=True))
        params = ep_info.get("parameters", {})
        if method == "POST":
            params.update(
                {"body": {"required": True, "type": "JSON"}, "fields": {"type": "JSON"}}
            )
        if not params:
            add_line("Endpoint takes no parameters")
        else:
            add_line("Parameters (*required):")
            for param_name in sorted(params):
                param = params[param_name]
                descr = param.get("description")
                descr = "\n" + wrapper.fill(descr) if descr else ""
                add_line(
                    "  {}: {} {} {}".format(
                        param_name,
                        param["type"],
                        "*" if param.get("required") else "",
                        descr,
                    )
                )
        return "\n".join(help_lines)

    def get_endpoints_info(self, endpoints):
        lines = []
        for name_parts in endpoints:
            descr = self.endpoints[name_parts].get("description", "")
            lines.append((" ".join(name_parts), descr.strip().split("\n")[0]))
        longest_name = max(len(l[0]) for l in lines)
        fmt = "  {{: <{}}}  {{}}".format(longest_name)
        return "\n".join(fmt.format(*l) for l in lines)

    def walk_endpoints(self, resource, parents=()):
        for ep_name, ep_info in resource.get("methods", {}).items():
            yield tuple(parents + (ep_name,)), ep_info
        for rsc_name, rsc in resource.get("resources", {}).items():
            for ep_name, ep_info in self.walk_endpoints(
                rsc, tuple(parents + (rsc_name,))
            ):
                yield ep_name, ep_info

    def _extract_from_discovery(self, name_parts):
        resources = self.discovery_doc.get("resources")
        if not resources:
            return None
        return _extract_from_discovery_spec(resources, name_parts)

    def _get_api_call(self, name_parts, params):
        """ Construct the call """
        endpoint = self._extract_from_discovery(name_parts)
        if not endpoint:
            raise ApiCallError(f"Endpoint {'/'.join(name_parts)} not found")
        verb = endpoint.get("httpMethod")
        body = params.get("body") if verb == "POST" else None
        url = self._api_url + "/" + "/".join(name_parts)
        resp = self.session.request(verb, url, params=params, json=body)
        resp.raise_for_status()
        return resp.json()

    def get_call(self, *name_parts, **params):
        """
        Args:
            *name_parts (List[str]): Endpoint, eg user/get or "user", "get"
            **params (dict): Parameters of the call

        Returns:
            Union[dict, List[dict]]: Object or objects returned by the endpoint call.

        Example:
            List feedtypes in LumApps:
            -> GET https://.../_ah/api/lumsites/v1/feedtype/list

            With this endpoint:

                >>> feedtypes = get_call("feedtype/list")
                >>> print(feedtypes)
        """
        if params is None:
            params = {}
        name_parts = _parse_endpoint_parts(name_parts)
        items = []
        cursor = None
        if "body" in params and isinstance(params["body"], str):
            params["body"] = loads(params["body"])
        while True:
            if cursor:
                if "body" in params:
                    params["body"]["cursor"] = cursor
                else:
                    params["cursor"] = cursor
            response = self._get_api_call(name_parts, params)
            if "more" in response and "items" not in response:
                return items  # empty list
            if "more" in response and "items" in response:
                items.extend(response["items"])
                if response.get("more", False):
                    cursor = response["cursor"]
                else:
                    return self._prune(name_parts, items)
            else:
                return self._prune(name_parts, response)

    def iter_call(self, *name_parts, **params):
        """
         Args:
            *name_parts (List[str]): Endpoint, eg user/get or "user", "get"
            **params (dict): Parameters of the call

        Yields:
            dict: Objects returned by the endpoint call.


        Example:
            List feedtypes in LumApps:
            -> GET https://.../_ah/api/lumsites/v1/feedtype/list

            With this endpoint:

                >>> feedtypes = iter_call("feedtype/list")
                >>> for feedtype in feedtypes: print(feedtype)
        """
        if params is None:
            params = {}
        name_parts = _parse_endpoint_parts(name_parts)
        cursor = None
        if "body" in params and isinstance(params["body"], str):
            params["body"] = loads(params["body"])
        while True:
            if cursor:
                if "body" in params:
                    params["body"]["cursor"] = cursor
                else:
                    params["cursor"] = cursor
            response = self._get_api_call(name_parts, params)
            if "more" in response and "items" not in response:
                return  # empty list
            if "more" in response and "items" in response:
                for item in response["items"]:
                    yield self._prune(name_parts, item)
                if response.get("more", False):
                    cursor = response["cursor"]
                else:
                    return
            else:
                yield self._prune(name_parts, response)

    def get_matching_endpoints(self, name_parts):
        # find exact matches of all parts up to but excluding last
        matches = [n for n in self.endpoints if len(n) >= len(name_parts)]
        for i, part in enumerate(name_parts[:-1]):
            matches = [n for n in matches if len(n) >= i and n[i] == part]
        # find 'startswith' matches of the last part
        last = name_parts[-1]
        idx = len(name_parts) - 1
        matches = [m for m in matches if len(m) >= idx and m[idx].startswith(last)]
        if not matches:
            return "Endpoint not found"
        return (
            "Endpoint not found. Did you mean one of these?\n"
            + self.get_endpoints_info(sorted(matches))
        )
