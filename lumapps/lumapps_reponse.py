"""A Python module for iteracting and consuming responses from LumApps."""

# Standard Imports
import logging
import asyncio

# Internal Imports
import lumapps.errors as e


class LumAppsResponse(object):
    """An iterable container of response data.
    Attributes:
        data (dict): The json-encoded content of the response. Along
            with the headers and status code information.
    Methods:
        validate: Check if the response from LumApps was successful.
        get: Retrieves any key from the response data.
        next: Retrieves the next portion of results,
            if 'next_cursor' is present.
    Example:
    ```python
    import os
    import LumApps
    client = LumApps.WebClient(token=os.environ['LumApps_API_TOKEN'])
    response1 = client.auth_revoke(test='true')
    assert not response1['revoked']
    response2 = client.auth_test()
    assert response2.get('ok', False)
    users = []
    for page in client.users_list(limit=2):
        users = users + page['members']
    ```
    Note:
        Some responses return collections of information
        like channel and user lists. If they do it's likely
        that you'll only receive a portion of results. This
        object allows you to iterate over the response which
        makes subsequent API requests until your code hits
        'break' or there are no more results to be found.
        Any attributes or methods prefixed with _underscores are
        intended to be "private" internal use only. They may be changed or
        removed at anytime.
    """

    def __init__(
        self,
        *,
        client,
        http_verb: str,
        api_url: str,
        req_args: dict,
        data: dict,
        headers: dict,
        status_code: int,
    ):
        self.http_verb = http_verb
        self.api_url = api_url
        self.req_args = req_args
        self.data = data
        self.headers = headers
        self.status_code = status_code
        self._client = client
        self._logger = logging.getLogger(__name__)

    def __str__(self):
        """Return the Response data if object is converted to a string."""
        return f"{self.data}"

    def __getitem__(self, key):
        """Retreives any key from the data store.
        Note:
            This is implemented so users can reference the
            LumAppsResponse object like a dictionary.
            e.g. response["ok"]
        Returns:
            The value from data or None.
        """
        return self.data.get(key, None)

    def __iter__(self):
        """Enables the ability to iterate over the response.
        It's required for the iterator protocol.
        Note:
            This enables LumApps cursor-based pagination.
        Returns:
            (LumAppsResponse) self
        """
        self._iteration = 0
        return self

    def __next__(self):
        """Retreives the next portion of results, if 'next_cursor' is present.
        Note:
            Some responses return collections of information
            like channel and user lists. If they do it's likely
            that you'll only receive a portion of results. This
            method allows you to iterate over the response until
            your code hits 'break' or there are no more results
            to be found.
        Returns:
            (LumAppsResponse) self
                With the new response data now attached to this object.
        Raises:
            LumAppsApiError: If the request to the LumApps API failed.
            StopIteration: If 'next_cursor' is not present or empty.
        """
        self._iteration += 1
        if self._iteration == 1:
            return self
        if self._next_cursor_is_present(self.data):

            if not self.req_args.get("params"):
                self.req_args["params"] = {}
            self.req_args["params"].update({"cursor": self.data["cursor"]})

            response = asyncio.get_event_loop().run_until_complete(
                self._client._request(
                    http_verb=self.http_verb,
                    api_url=self.api_url,
                    req_args=self.req_args,
                )
            )
            self.data = response["data"]
            self.headers = response["headers"]
            self.status_code = response["status_code"]
            return self.validate()
        else:
            raise StopIteration

    def get(self, key, default=None):
        """Retreives any key from the response data.
        Note:
            This is implemented so users can reference the
            LumAppsResponse object like a dictionary.
            e.g. response.get("ok", False)
        Returns:
            The value from data or the specified default.
        """
        return self.data.get(key, default)

    @property
    def is_iterable(self):
        return self._next_cursor_is_present(self.data)

    def validate(self):
        """Check if the response from LumApps was successful.
        Returns:
            (LumAppsResponse)
                This method returns it's own object. e.g. 'self'
        Raises:
            LumAppsApiError: The request to the LumApps API failed.
        """
        if self.status_code == 200 and self.data:
            self._logger.debug(
                "Received the following response: %s", self.data
            )
            return self
        msg = "The request to the LumApps API failed."
        raise e.LumAppsApiError(message=msg, response=self.data)

    @staticmethod
    def _next_cursor_is_present(data):
        """Determine if the response contains 'cursor'
        and 'cursor' is not empty.
        Returns:
            A boolean value.
        """
        present = (
            data.get("more", False)
            and "cursor" in data
            and data.get("cursor", None) is not None
            and data.get("cursor", "") != ""
        )
        return present
