from typing import List, Generator

from lumapps.base_client import LumAppsBaseClient


class LumAppsApiClient(LumAppsBaseClient):
    DISCOVERY_URL = "https://lumsites.appspot.com/_ah/api/discovery/v1/apis/lumsites/v1/rest"

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

    def iter_pages(self, api_endpoint: str) -> Generator[List[dict]]:
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

    def iter_entities(self, api_endpoint: str) -> Generator[dict]:
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

    # def get_call(self, *method_parts, **params):
    #     api_endpoint = "/".join(method_parts)
    #     res = self.api_call(api_endpoint, "GET")
