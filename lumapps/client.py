from lumapps.base_client import LumAppsBaseClient


class LumAppsApiClient(LumAppsBaseClient):
    def list_all(self, api_endpoint: str):
        """

        Args:
            api_endpoint (str): The target LumApps API endpoint on which to do the list.
                                eg 'user'
        Returns:
            list: The entire data resulting of the call
        """
        splitted = api_endpoint.split("/")
        api_endpoint = (
            api_endpoint + "/list" if splitted[-1] != "list" else api_endpoint
        )
        pages = self.api_call(api_endpoint, "GET")
        _data = [page.get("items", []) for page in pages]
        data = [item for sublist in _data for item in sublist]
        return data

    def iter_list(self, api_endpoint: str):
        """

        Args:
            api_endpoint (str): The target LumApps API endpoint. eg 'user'
        Returns:
            list: The data as an iterator where each step is a page of 30 results
        """
        splitted = api_endpoint.split("/")
        api_endpoint = (
            api_endpoint + "/list" if splitted[-1] != "list" else api_endpoint
        )
        pages = self.api_call(api_endpoint, "GET")
        for page in pages:
            items = page.get("items", [])
            for i in items:
                yield i
