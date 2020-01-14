class ApiClientError(Exception):
    """ Base error of the ApiClient """


class ApiCallError(ApiClientError):
    """ Retrocomptiblity """


class ApiClientRequestError(ApiClientError):
    """ Error during a request with the ApiClient """
