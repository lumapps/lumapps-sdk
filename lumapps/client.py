from typing import List, Generator

from lumapps.base_client import LumAppsBaseClient
from lumapps.errors import LumAppsRequestError, LumAppsClientError


class LumAppsApiClient(LumAppsBaseClient):
    def list_all(self, api_endpoint: str) -> List[dict]:
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
    ) -> Generator[List[dict], None, None]:
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
            # spec_type = "swagger"
            # Parse spec
            pass
        else:
            raise LumAppsClientError("Unknwon spec type")

    def _extract_method_from_discovery(self, *method_parts):

        resources = self.api_spec.get("resources")

        if not resources:
            return

        getted = None
        for i, part in enumerate(method_parts):
            if i == len(method_parts) - 2:
                getted = resources.get(part, {})
            elif i == len(method_parts) - 1:
                getted = getted.get("methods", {}).get(part, {})
            else:
                if not getted:
                    getted = resources.get(part, {}).get("resources", {})
                getted = getted.get(part, {}).get("resources", {})
        return getted

    def get_call(self, *method_parts, **params):
        """
        """
        api_endpoint = "/".join(method_parts)
        # last_part = method_parts[-1]

        method = self._extract_method_from_discovery(method_parts)
        if not method:
            raise LumAppsRequestError(
                f"Could not find the endpoint {api_endpoint}"
            )

        print(f"Found method {method} for endpoint {api_endpoint}")
