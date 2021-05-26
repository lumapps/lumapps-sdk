from functools import wraps
from logging import debug
from typing import Sequence

from httpx import HTTPStatusError

from lumapps.api.errors import (
    FeedsRequiredError,
    UrlAlreadyExistsError,
    get_http_err_content,
)


def none_on_http_codes(codes=(404,)):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except HTTPStatusError as e:
                if e.response.status_code in codes:
                    return None
                raise

        return wrapper

    return decorator


def retry_on_http_status_error(max_attempts=3):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            attempts = 0
            while True:
                attempts += 1
                try:
                    return f(*args, **kwargs)
                except HTTPStatusError as e:
                    if attempts >= max_attempts:
                        debug(f"Max attempts {max_attempts} reached")
                        raise
                    code = e.response.status_code
                    debug(f"{attempts}/{max_attempts} failed: HTTP {code}")
                    continue

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
                except HTTPStatusError as e:
                    if attempts >= max_attempts:
                        debug(f"Max attempts {max_attempts} reached")
                        raise
                    code = e.response.status_code
                    if code in codes:
                        debug(f"{attempts}/{max_attempts} failed: HTTP {code}")
                        continue
                    raise

        return wrapper

    return decorator


def none_on_404(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    return wrapper


def false_on_404(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            function(*args, **kwargs)
            return True
        except HTTPStatusError as e:
            if e.response.status_code == 404:
                return False
            raise

    return wrapper


def none_on_code_and_message(code: int, message: str):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except HTTPStatusError as e:
                if e.response.status_code == code:
                    e_str = get_http_err_content(e)
                    if message in e_str:
                        return None
                raise

        return wrapper

    return decorator


def none_on_400_ALREADY_ARCHIVED(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except HTTPStatusError as e:
            if e.response.status_code == 400:
                e_str = get_http_err_content(e)
                if "ALREADY_ARCHIVED" in e_str:
                    return None
            raise

    return wrapper


def none_on_400_SUBSCRIPTION_ALREADY_EXISTS_OR_PINNED(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except HTTPStatusError as e:
            if e.response.status_code == 400:
                e_str = get_http_err_content(e)
                if "SUBSCRIPTION_ALREADY_EXISTS" in e_str:
                    return None
                if "Already pinned" in e_str:
                    return None
            raise

    return wrapper


def raise_known_save_errors(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        try:
            return function(*args, **kwargs)
        except HTTPStatusError as e:
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
            if e.response.status_code == 400:
                e_str = get_http_err_content(e)
                if "URL_ALREADY_EXISTS" in e_str:
                    raise UrlAlreadyExistsError(e)
                if "Feeds are required" in e_str:
                    raise FeedsRequiredError(e)
            raise

    return wrapper
