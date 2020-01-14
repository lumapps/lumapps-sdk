class ApiClientError(Exception):
    """ Base error of the ApiClient """


class ApiCallError(ApiClienError):
    """ Retrocomptiblity """


class ApiClientRequestError(ApiClientError):
    """ Error during a request with the ApiClient """
