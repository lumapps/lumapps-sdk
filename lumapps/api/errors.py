from functools import wraps
from logging import debug
from typing import Sequence

from httpx import HTTPError


def get_http_err_content(e: HTTPError) -> str:
    try:
        return e.response.content.decode()  # type: ignore
    except AttributeError:
        return ""


class BaseClientError(Exception):
    """ Base error of the BaseClient """


class BadCallError(BaseClientError):
    """ Retrocompatiblity """


class LumAppsClientError(BaseClientError):
    def __init__(self, code, message=None):
        super().__init__(message)
        self.code = code


class LumAppsClientConfError(BaseClientError):
    def __init__(self, message=None):
        super().__init__(message)


class MissingMetadataError(LumAppsClientError):
    def __init__(self, message):
        super().__init__("MISSING_METADATA", message)


class FileUploadError(LumAppsClientError):
    def __init__(self, message):
        super().__init__("FILE_UPLOAD", message)


class FolderCreationError(LumAppsClientError):
    def __init__(self, message):
        super().__init__("FILE_UPLOAD", message)


class FileDownloadError(LumAppsClientError):
    def __init__(self, message):
        super().__init__("FILE_DOWNLOAD", message)


class NonIdpGroupInCommunityError(LumAppsClientError):
    def __init__(self, message):
        super().__init__("NON_IDP_GROUP_IN_COMMUNITY", message)


class FeedsRequiredError(LumAppsClientError):
    def __init__(self, message):
        super().__init__("FEEDS_REQUIRED", message)


class UrlAlreadyExistsError(LumAppsClientError):
    def __init__(self, message):
        super().__init__("URL_ALREADY_EXISTS", message)


class GetTokenError(LumAppsClientError):
    def __init__(self, message):
        super().__init__("GET_TOKEN", message)


class UserCannotSaveError(LumAppsClientError):
    def __init__(self, message):
        super().__init__("USER_CANNOT_SAVE", message)


def none_on_http_codes(codes=(404,)):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except HTTPError as e:
                try:
                    if e.response.status_code in codes:
                        return None
                except AttributeError:
                    pass
                raise

        return wrapper

    return decorator


def retry_on_http_codes(codes: Sequence = (), max_attempts=3):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            attempts = 0
            while True:
                attempts += 1
                try:
                    return f(*args, **kwargs)
                except HTTPError as e:
                    if attempts >= max_attempts:
                        debug(f"Max attempts {max_attempts} reached")
                        raise
                    try:
                        code = e.response.status_code
                        if code in codes:
                            debug(f"{attempts}/{max_attempts} failed: HTTP {code}")
                            continue
                    except AttributeError:
                        pass
                    raise

        return wrapper

    return decorator


def none_on_404(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except HTTPError as e:
            try:
                if e.response.status_code == 404:
                    return None
            except AttributeError:
                pass
            raise

    return wrapper


def false_on_404(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            function(*args, **kwargs)
            return True
        except HTTPError as e:
            try:
                if e.response.status_code == 404:
                    return False
            except AttributeError:
                pass
            raise

    return wrapper


def none_on_400_ALREADY_ARCHIVED(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except HTTPError as e:
            try:
                if e.response.status_code == 400:
                    e_str = get_http_err_content(e)
                    if "ALREADY_ARCHIVED" in e_str:
                        return None
            except AttributeError:
                pass
            raise

    return wrapper


def none_on_400_SUBSCRIPTION_ALREADY_EXISTS_OR_PINNED(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except HTTPError as e:
            try:
                if e.response.status_code == 400:
                    e_str = get_http_err_content(e)
                    if "SUBSCRIPTION_ALREADY_EXISTS" in e_str:
                        return None
                    if "Already pinned" in e_str:
                        return None
            except AttributeError:
                pass
            raise

    return wrapper


def raise_known_save_errors(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except HTTPError as e:
            """
            {
                "error": {
                    "code": 400,
                    "errors": [
                        {
                            "domain": "global",
                            "message": "URL_ALREADY_EXISTS",
                            "reason": "badRequest"
                        }
                    ],
                    "message": "URL_ALREADY_EXISTS"
                }
            }
            {
                "error": {
                    "code": 400,
                    "errors": [
                        {
                            "domain": "global",
                            "message": "Feeds are required",
                            "reason": "badRequest"
                        }
                    ],
                    "message": "Feeds are required"
                }
            }
            """
            try:
                if e.response.status_code == 400:
                    e_str = get_http_err_content(e)
                    if "URL_ALREADY_EXISTS" in e_str:
                        raise UrlAlreadyExistsError(e)
                    if "Feeds are required" in e_str:
                        raise FeedsRequiredError(e)
            except AttributeError:
                pass
            raise

    return wrapper
