from contextlib import AbstractContextManager
from functools import lru_cache
from json import dumps, loads
from pathlib import Path
from textwrap import TextWrapper
from time import time
from typing import (
    IO,
    Any,
    Callable,
    Dict,
    Generator,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from httpx import Client

# from authlib.integrations.requests_client import OAuth2Session, AssertionSession
from lumapps.api.authlib_helpers import AssertionClient, OAuth2Client
from lumapps.api.errors import BadCallError, BaseClientError
from lumapps.api.utils import (
    FILTERS,
    GOOGLE_APIS,
    _parse_endpoint_parts,
    get_discovery_cache,
    get_endpoints,
    method_from_discovery,
    pop_matches,
)

LUMAPPS_SCOPE = ["https://www.googleapis.com/auth/userinfo.email"]
LUMAPPS_VERSION = "v1"
LUMAPPS_NAME = "lumsites"
LUMAPPS_BASE_URL = "https://lumsites.appspot.com"
FileContent = Union[IO[str], IO[bytes], str, bytes]


class BaseClient(AbstractContextManager):
    def __init__(
        self,
        auth_info: Optional[Dict[str, Any]] = None,
        api_info: Optional[Dict[str, Any]] = None,
        user: Optional[str] = None,
        token: Optional[str] = None,
        token_getter: Optional[Callable[[], Tuple[str, int]]] = None,
        prune: bool = False,
        no_verify: bool = False,
        proxy_info: Optional[Dict[str, Any]] = None,
    ):
        """
            Args:
                auth_info: When specified, a service account or a web auth JSON dict.
                api_info: When specified, a JSON dict containing the description of your
                    api. Defaults to LumApps API.
                user: Email of user on behalf of whom to authenticate using domain-wide
                    delegation.
                token: A bearer access token.
                token_getter: A bearer access token getter function.
                prune: Whether or not to use FILTERS to prune LumApps API responses.
                no_verify: Disables SSL verification.
                proxy_info: When specified, a JSON dict with proxy parameters.
        """
        self._token_expiry = 0
        self.no_verify = no_verify
        self.proxy_info = proxy_info
        self.prune = prune
        self._auth_info = auth_info
        self._token = None
        self._endpoints = None
        self._client = None
        self._headers: dict = {}
        if api_info is None:
            api_info = {}
        api_info.setdefault("name", LUMAPPS_NAME)
        api_info.setdefault("version", LUMAPPS_VERSION)
        api_info.setdefault("base_url", LUMAPPS_BASE_URL)
        api_info.setdefault("scopes", LUMAPPS_SCOPE)
        self.api_info = api_info
        api_name = api_info["name"]
        self._scope = " ".join(api_info["scopes"])
        api_ver = api_info["version"]
        prefix = "" if api_name in GOOGLE_APIS else "/_ah/api"
        self._api_url = f"{prefix}/{api_name}/{api_ver}"
        self._discovery_url = (
            f"{self.base_url}{prefix}/discovery/v1/apis/{api_name}/{api_ver}/rest"
        )
        self.token_getter = token_getter
        self.user = user
        self.token = token
        self.cursor = None

    def __exit__(self, *exc):
        self.close()
        return False

    def close(self):
        if self._client:
            self._client.close()
            self._client = None

    @property
    def base_url(self):
        return self.api_info["base_url"].rstrip("/")

    @property
    def token(self):
        return self._token

    @token.setter
    def token(self, v):
        if self._token and self._token == v:
            return
        self._token = v
        self._headers["authorization"] = f"Bearer {self._token}"
        if self._client:
            self._client.headers.update(self._headers)

    def _create_client(self):
        auth = self._auth_info
        kwargs = {
            "base_url": self.base_url,
            "headers": self._headers,
            "verify": not self.no_verify,
            "timeout": 120,
        }
        if self.proxy_info:
            scheme = self.proxy_info.get("scheme", "https")
            host = self.proxy_info["host"]
            port = self.proxy_info["port"]
            user = self.proxy_info.get("user") or ""
            pwd = self.proxy_info.get("password") or ""
            if user or pwd:
                proxy = f"{scheme}://{user}:{pwd}@{host}:{port}"
            else:
                proxy = f"{scheme}://{host}:{port}"
            kwargs["proxies"] = {"https://": proxy, "http://": proxy}
        else:
            kwargs["proxies"] = None
        if not auth and self._token:
            s = Client(**kwargs)
        elif auth and "refresh_token" in auth:
            s = OAuth2Client(
                client_id=auth["client_id"],
                client_secret=auth["client_secret"],
                scope=self._scope,
                **kwargs,
            )
            s.refresh_token(auth["token_uri"], refresh_token=auth["refresh_token"])
        elif auth:  # service account
            claims = {"scope": self._scope} if self._scope else {}
            s = AssertionClient(
                token_endpoint=auth["token_uri"],
                issuer=auth["client_email"],
                audience=auth["token_uri"],
                claims=claims,
                subject=self.user,
                key=auth["private_key"],
                header={"alg": "RS256"},
                **kwargs,
            )
        else:
            raise BaseClientError(
                "No authentication provided (token_getter, auth_info, or token)."
            )
        return s

    @property
    def client(self) -> Client:
        """Setup the client object."""
        self._check_access_token()
        if self._client is None:
            self._client = self._create_client()
        return self._client

    @property  # type: ignore
    @lru_cache()
    def discovery_doc(self):
        url = self._discovery_url
        d = get_discovery_cache().get(url)
        if d and isinstance(d, str):
            return loads(d)
        elif d and isinstance(d, dict):
            return d
        else:
            resp = self.client.get(url)
            resp_doc = resp.json()
            get_discovery_cache().set(url, resp_doc)
            return resp_doc

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

    def get_new_client_as_using_dwd(self, user_email: str) -> "BaseClient":
        """ Get a new BaseClient using domain-wide delegation """
        return BaseClient(
            auth_info=self._auth_info,
            api_info=self.api_info,
            user=user_email,
            no_verify=self.no_verify,
            proxy_info=self.proxy_info,
            prune=self.prune,
        )

    def get_new_client_as(
        self, user_email: str, customer_id: Optional[str] = None
    ) -> "BaseClient":
        """ Get a new BaseClient using an authorized client account by obtaining a
            token using the user/getToken endpoint.

            Args:
                user_email (str): User you want to authenticate on behalf of
                customer_id (str): Id of the LumApps customer the user belong to

            Returns:
                BaseClient: A new instance of the BaseClient correctly authenticated.
        """
        client = BaseClient(
            auth_info=self._auth_info,
            api_info=self.api_info,
            no_verify=self.no_verify,
            proxy_info=self.proxy_info,
            prune=self.prune,
        )
        token_infos: Any = client.get_call(
            "user/getToken", customerId=customer_id, email=user_email
        )
        token = token_infos["accessToken"]
        return BaseClient(
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
            self._endpoints = get_endpoints(self.discovery_doc)
        return self._endpoints

    def get_help(self, name_parts, debug=False):
        help_lines = []

        def add_line(li):
            help_lines.append(li)

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
                {
                    "body": {"required": True, "type": "JSON"},
                    "fields": {"type": "JSON"},
                }
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
        longest_name = max(len(li1[0]) for li1 in lines)
        fmt = "  {{: <{}}}  {{}}".format(longest_name)
        return "\n".join(fmt.format(*li2) for li2 in lines)

    def _expand_path(self, path, endpoint: dict, params: dict):
        param_specs = endpoint.get("parameters", {})
        path_args: dict = {}
        for param, specs in param_specs.items():
            if specs.get("required") is True and param not in params:
                raise BadCallError(f"Missing required parameter {param}")
            if specs["location"] == "path":
                path_args[param] = None
        if path_args:
            for param in path_args:
                path_args[param] = params.pop(param)
            path = path.format(**path_args)
        return path

    @lru_cache()
    def _get_endpoint_and_path_from_discovery(self, name_parts):
        endpoint = method_from_discovery(self.discovery_doc, name_parts)
        if not endpoint:
            raise BadCallError(f"Endpoint {'.'.join(name_parts)} not found")
        if endpoint.get("mediaUpload"):
            raise BadCallError(
                f"Endpoint {'.'.join(name_parts)} is for uploads, "
                f"use upload_call method instead of get_call or iter_call"
            )
        path = self._api_url + "/" + endpoint.get("path") or "/".join(name_parts)
        return endpoint, path

    def _get_verb_path_params(self, name_parts, params: dict):
        endpoint, path = self._get_endpoint_and_path_from_discovery(tuple(name_parts))
        path = self._expand_path(path, endpoint, params)
        verb = endpoint.get("httpMethod")
        return verb, path, params

    def _call(self, name_parts: Sequence[str], params: dict, json=None):
        """ Construct the call """
        verb, path, params = self._get_verb_path_params(name_parts, params)
        resp = self.client.request(verb, path, params=params, json=json)
        resp.raise_for_status()
        if not resp.content:
            return None
        return resp.json()

    @staticmethod
    def _pop_body(params: dict):
        body = params.pop("body", None)
        body = loads(body) if isinstance(body, str) else body
        return body

    def upload(self, file_content: FileContent, metadata: dict, *name_parts, **params):
        name_parts = _parse_endpoint_parts(name_parts)
        endpoint: Any = method_from_discovery(self.discovery_doc, name_parts)  # type: ignore  # noqa
        if not endpoint.get("mediaUpload"):
            raise BadCallError(
                f"Endpoint {'.'.join(name_parts)} is not for uploads, "
                f"use get_call or iter_call instead."
            )
        verb = endpoint.get("httpMethod")
        upload_specs = endpoint["mediaUpload"]["protocols"]["simple"]
        path: Any = self.discovery_doc["rootUrl"].rstrip("/") + upload_specs["path"]  # type: ignore  # noqa
        path = self._expand_path(path, endpoint, params)
        files = {
            "data": ("metadata", dumps(metadata), "application/json; charset=UTF-8"),
            "file": file_content,
        }
        resp = self.client.request(verb, path, params=params, files=files)
        resp.raise_for_status()
        return resp.json()

    def upload_call(
        self, fpath: Union[Path, str], metadata: dict, *name_parts, **params
    ):
        with Path(fpath).open("rb") as fh:
            return self.upload(fh, metadata, *name_parts, **params)

    def get_call(
        self, *name_parts, **params
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], None]:
        """Generic function to call a lumapps endpoint

            Args:
                *name_parts: Endpoint, eg user/get or "user", "get"
                **params: Parameters of the call

            Returns:
                Object or objects returned by the endpoint call.

            Example:
                List feedtypes in LumApps:
                -> GET https://.../_ah/api/lumsites/v1/feedtype/list

                With this endpoint:

                    >>> feedtypes = get_call("feedtype/list")
                    >>> print(feedtypes)
        """
        name_parts = _parse_endpoint_parts(name_parts)
        items: List[dict] = []
        self.cursor = cursor = params.pop("cursor", None)
        body = self._pop_body(params)
        while True:
            if cursor:
                if body is not None:
                    body["cursor"] = cursor
                else:
                    params["cursor"] = cursor
            response = self._call(name_parts, params, body)
            if response is None:
                return None

            more = response.get("more")
            response_items = response.get("items")
            if more:
                if response_items:
                    self.cursor = cursor = response["cursor"]
                    items.extend(response_items)
                else:
                    # No results but a more field set to true ...
                    # ie, the api return something wrong
                    self.cursor = cursor = None
                    return self._prune(name_parts, items)
            else:
                # No more result to get
                if response_items:
                    self.cursor = cursor = None
                    items.extend(response_items)
                    return self._prune(name_parts, items)
                else:
                    # No results, return
                    self.cursor = cursor = None
                    # special case of
                    return [] if more is False else self._prune(name_parts, response)

    def iter_call(
        self, *name_parts, **params
    ) -> Generator[
        Union[Dict[str, Any], List[Dict[str, Any]]],
        Union[Dict[str, Any], List[Dict[str, Any]]],
        None,
    ]:
        """
            Args:
                *name_parts: Endpoint, eg user/get or "user", "get"
                **params: Parameters of the call

            Yields:
                Objects returned by the endpoint call


            Example:
                List feedtypes in LumApps:
                -> GET https://.../_ah/api/lumsites/v1/feedtype/list

                With this endpoint:

                    >>> feedtypes = iter_call("feedtype/list")
                    >>> for feedtype in feedtypes: print(feedtype)
        """
        name_parts = _parse_endpoint_parts(name_parts)
        self.cursor = cursor = params.pop("cursor", None)
        body = self._pop_body(params)
        while True:
            if cursor:
                if body is not None:
                    body["cursor"] = cursor
                else:
                    params["cursor"] = cursor

            response = self._call(name_parts, params, body)
            more = response.get("more")
            items = response.get("items")

            if more:
                if items:
                    # Yield the results and continue the loop
                    self.cursor = cursor = response["cursor"]
                    for item in items:
                        yield self._prune(name_parts, item)
                else:
                    # No results but a more field set to true ...
                    # ie, the api return something wrong
                    self.cursor = cursor = None
                    return
            else:
                # No more result to get
                if items:
                    # Yield the last results and then return
                    self.cursor = cursor = None
                    for item in items:
                        yield self._prune(name_parts, item)
                    else:
                        return
                else:
                    # No results, return
                    self.cursor = cursor = None
                    return

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
