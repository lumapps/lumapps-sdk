from json import loads, dumps
from time import time
from textwrap import TextWrapper

from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials

from lumapps.api.errors import ApiClientError, ApiCallError
from lumapps.api.utils import (
    DiscoveryCache,
    pop_matches,
    GOOGLE_APIS,
    FILTERS,
    _parse_endpoint_parts,
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
        no_verify=False,
        proxy_info=None,
    ):
        self._get_token_user = None
        self._token_expiry = 0
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
            prefix = f"{self.base_url}"
        else:
            prefix = f"{self.base_url}/_ah/api"
        api_name, api_version = self._api_name, self._api_version
        self._api_url = f"{prefix}/{api_name}/{api_version}"
        self._discovery_url = (
            f"{prefix}/discovery/v1/apis/{api_name}/{api_version}/rest"
        )
        self._endpoints = None
        self._session = None
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
        elif auth_info:  # session account
            self.creds = service_account.Credentials.from_service_account_info(
                auth_info
            )
            if self._api_scopes:
                self.creds = self.creds.with_scopes(self._api_scopes)
            if user:
                self.creds = self.creds.with_subject(user)
        else:
            raise ApiClientError(
                "You must provide authentication infos (token_getter, "
                "auth_info, credentials or token)."
            )
        self.email = user or ""
        self._discovery_doc = None

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
        for filter_method in FILTERS:
            filter_method_parts = filter_method.split("/")
            if len(name_parts) != len(filter_method_parts):
                continue
            for filter_part, part in zip(filter_method_parts, name_parts):
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

    def get_new_client_as_using_dwd(self, user_email):
        """ Get a new ApiClient using domain-wide delegation """
        return ApiClient(
            auth_info=self._auth_info,
            api_info=self.api_info,
            user=user_email,
            no_verify=self.no_verify,
            proxy_info=self.proxy_info,
            prune=self.prune,
        )

    def get_new_client_as(self, user_email, customer_id=None):
        """ Get a new ApiClient using an authorized session account by obtaining a
            token using the user/getToken method.

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
    def token(self):
        if not self.creds.token:
            self.session.get(self.base_url)
        return self.creds.token

    @token.setter
    def token(self, v):
        if self.creds and self.creds.token == v:
            return
        self._session = None
        self.creds = Credentials(v)

    @property
    def session(self):
        """Setup the session object.
        """
        self._check_access_token()
        if self._session is None:
            s = AuthorizedSession(self.creds)
            s.verify = not self.no_verify
            if self.proxy_info:
                scheme = self.proxy_info.get("scheme", "https")
                host = self.proxy_info["host"]
                port = self.proxy_info["port"]
                user = self.proxy_info["user"]
                pwd = self.proxy_info["password"]
                s.proxies.update({"https": f"{scheme}://{user}:{pwd}@{host}:{port}"})
                s.proxies.update({"http": f"{scheme}://{user}:{pwd}@{host}:{port}"})
            self._session = s
        return self._session

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
        method = self.endpoints[name_parts]
        add_line(
            method.get("httpMethod", "?") + " method: " + " ".join(name_parts) + "\n"
        )
        if "description" in method:
            add_line(method["description"].strip() + "\n")
        if debug:
            add_line(dumps(method, indent=4, sort_keys=True))
        params = method.get("parameters", {})
        if method.get("httpMethod", "") == "POST":
            params.update(
                {"body": {"required": True, "type": "JSON"}, "fields": {"type": "JSON"}}
            )
        if not params:
            add_line("API method takes no parameters")
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

    def get_method_descriptions(self, endpoints):
        lines = []
        for name_parts in endpoints:
            method = self.endpoints[name_parts]
            lines.append(
                (
                    " ".join(name_parts),
                    method.get("description", "").strip().split("\n")[0],
                )
            )
        longest_name = max(len(l[0]) for l in lines)
        fmt = "  {{: <{}}}  {{}}".format(longest_name)
        return "\n".join(fmt.format(*l) for l in lines)

    def walk_endpoints(self, resource, parents=()):
        for method_name, method in resource.get("methods", {}).items():
            yield tuple(parents + (method_name,)), method
        for rsc_name, rsc in resource.get("resources", {}).items():
            for method_name, method in self.walk_endpoints(
                rsc, tuple(parents + (rsc_name,))
            ):
                yield method_name, method

    def _extract_from_discovery(self, name_parts):
        resources = self.discovery_doc.get("resources")
        if not resources:
            return
        getted = None
        for i, part in enumerate(name_parts):
            if i == len(name_parts) - 2:
                getted = resources.get(part, {})
            elif i == len(name_parts) - 1:
                if not getted:
                    getted = resources.get(part, {}).get("methods", {})
                getted = getted.get("methods", {}).get(part, {})
            else:
                if not getted:
                    getted = resources.get(part, {}).get("resources", {})
                getted = getted.get(part, {}).get("resources", {})
        return getted

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
            *name_parts (List[str]): The LumApps API endpoint (eg user/get or "user", "get").
            **params (dict): Parameters of the call

        Returns:
            Union[dict, List[dict]]: Object or list of objects returned by the LumApps API endpoint.

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
                self.last_cursor = None
                return items  # empty list
            if "more" in response and "items" in response:
                items.extend(response["items"])
                if response.get("more", False):
                    self.last_cursor = cursor = response["cursor"]
                else:
                    return self._prune(name_parts, items)
            else:
                self.last_cursor = None
                return self._prune(name_parts, response)

    def iter_call(self, *name_parts, **params):
        """
         Args:
            *name_parts (List[str]): The LumApps API endpoint (eg user/get or "user", "get").
            **params (dict): Parameters of the call

        Yields:
            dict: Object returned by the LumApps API endpoint.


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
            "Endpoint not found. Did you mean any of these?\n"
            + self.get_method_descriptions(sorted(matches))
        )
