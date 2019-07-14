"""A Python module for managing any LumApps client errors."""


class LumAppsClientError(Exception):
    """Base class for Client errors"""


class LumAppsRequestError(LumAppsClientError):
    """Error raised when there's a problem with the request that's being submitted.
    """

    pass


class LumAppsApiError(LumAppsClientError):
    """Error raised when LumApps does not send the expected response."""

    def __init__(self, message, response):
        msg = f"{message}\nThe server responded with: {response}"
        self.response = response
        super(LumAppsApiError, self).__init__(msg)


class LumAppsClientNotConnectedError(LumAppsClientError):
    """Error raised when attempting to send messages over the websocket when the
    connection is closed. """

    pass


class LumAppsObjectFormationError(LumAppsClientError):
    """Error raised when a constructed object is not valid/malformed"""
