import asyncio

from typing import Any, List, Dict, Generator, Union

from lumapps.base_client import LumAppsBaseClient
from lumapps.errors import LumAppsRequestError, LumAppsClientError
from lumapps.lumapps_reponse import LumAppsResponse


class LumAppsApiClient(LumAppsBaseClient):
    def list_all(self, api_endpoint: str) -> List[Dict[Any, Any]]:
        """ A method to call a /list endpoint and obtain all results in a list

        Args:
            api_endpoint (str): The target LumApps API endpoint on which to do the list.
                                eg 'user'
        Returns:
            List[dict]: The entire data resulting of the call
        """
        pages = self.api_call(self._parse_list_endpoint(api_endpoint), "GET")
        _data = [page.get("items", []) for page in pages]
        data = [item for sublist in _data for item in sublist]
        return data

    def iter_pages(
        self, api_endpoint: str
    ) -> Generator[List[Dict[Any, Any]], None, None]:
        """ A method to call a /list endpoint and obtain a generator that will
            gradually give you each result page

        Args:
            api_endpoint (str): The target LumApps API endpoint. eg 'user'

        Yield:
            List[dict]: A page of results, ie a list of entities
        """
        pages = self.api_call(self._parse_list_endpoint(api_endpoint), "GET")
        for page in pages:
            yield page

    def iter_entities(self, api_endpoint: str) -> Generator[dict, None, None]:
        """A method to call a /list endpoint and obtain a generator that will
            gradually give you each result entity

        Args:
            api_endpoint (str): The target LumApps API endpoint. eg 'user'

        Yield:
            dict: An entity present in the data resulting of the call
        """
        pages = self.api_call(self._parse_list_endpoint(api_endpoint), "GET")
        for page in pages:
            items = page.get("items", [])
            for i in items:
                yield i

    @staticmethod
    def _parse_list_endpoint(api_endpoint: str) -> str:
        splitted = api_endpoint.split("/")
        api_endpoint = (
            api_endpoint + "/list" if splitted[-1] != "list" else api_endpoint
        )
        return api_endpoint

    def extract_method_from_spec(self, *method_parts):
        if self.api_spec.get("discoveryVersion"):
            return self._extract_method_from_discovery(method_parts)
        elif self.api_spec.get("swagger"):
            # Parse spec
            pass
        else:
            raise LumAppsClientError("Unknwon spec type")

    def _extract_method_from_discovery(self, *method_parts):

        if isinstance(method_parts[0], tuple):
            method_parts = method_parts[0]

        resources = self.api_spec.get("resources")
        if not resources:
            return

        getted = None

        for i, part in enumerate(method_parts):
            if i == len(method_parts) - 2:
                getted = resources.get(part, {})
            elif i == len(method_parts) - 1:
                if not getted:
                    getted = resources.get(part, {}).get("methods", {})
                getted = getted.get("methods", {}).get(part, {})
            else:
                if not getted:
                    getted = resources.get(part, {}).get("resources", {})
                getted = getted.get(part, {}).get("resources", {})
        return getted

    def _generic_call(self, method_parts, params) -> LumAppsResponse:
        if len(method_parts) == 1:
            method_parts = tuple(method_parts[0].split("/"))

        api_endpoint = "/".join(method_parts)

        method = self._extract_method_from_discovery(method_parts)
        if not method:
            raise LumAppsRequestError(
                f"Could not find the endpoint {api_endpoint}"
            )

        http_verb = method.get("httpMethod")
        if not http_verb:
            raise LumAppsRequestError(
                f"Could not find the http method for the endpoint {api_endpoint}"
            )

        if http_verb == "GET":
            res = self.api_call(api_endpoint, "GET", params=params)
        elif http_verb == "POST":
            body = params.get("body")
            if not body:
                raise LumAppsClientError(f"No body given for a POST endpoint")
            del params["body"]
            res = self.api_call(api_endpoint, "POST", params=params, json=body)
        else:
            raise LumAppsClientError(f"Http method {http_verb} not supported")

        if isinstance(res, asyncio.Future):
            if self._event_loop is None:
                self._event_loop = self._get_event_loop()
            return self._event_loop.run_until_complete(res)

        return res

    def get_call(
        self, *method_parts, **params
    ) -> Union[LumAppsResponse, List[Dict[Any, Any]]]:
        """
            Returns:
                list[dict]: a list containing all the data resulting of the query

            Examples:
                To get a the user test@test.com via the user/get endpoint
                ```python
                    client = LumAppsApiClient()
                    user = client.get_call("user", "get", email="test@test.com")
                    print(user[0])
                ```
                To list french communities you do
                ```python
                    client = LumAppsApiClient()
                    communities = communities.iter_call("community", "list", fields="items(id, name)", body={"lang": "fr"})
                    for community in communities:
                        print(community)
                ````
                This example illustrate how to call a POST endpoint.
        """
        res = self._generic_call(method_parts, params)

        if res.is_iterable:
            _data = [page.get("items", []) for page in res]
            data = [item for sublist in _data for item in sublist]
            return data
        else:
            return res

    def iter_call(
        self, *method_parts, **params
    ) -> Generator[LumAppsResponse, None, None]:
        """

            Yields:
                dict: An entity of the data resutling of the request

            Examples:
                To get a the user test@test.com via the user/get endpoint
                ```python
                    client = LumAppsApiClient()
                    user = client.get_call("user", "get", email="test@test.com")
                    print(user[0])
                ```

                To list french communities you do
                ```python
                    client = LumAppsApiClient()
                    communities = communities.iter_call("community", "list", fields="items(id, name)", body={"lang": "fr"})
                    for community in communities:
                        print(community)
                ````
                This example illustrate how to call a POST endpoint.
        """
        res = self._generic_call(method_parts, params)

        if res.is_iterable:
            for page in res:
                items = page.get("items", [])
                for i in items:
                    yield i
        else:
            yield res
