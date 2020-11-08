import time
from dataclasses import dataclass
from functools import wraps
from logging import debug
from typing import Sequence, Tuple, Type

from httpx import HTTPStatusError

from lumapps.api.errors import (
    FeedsRequiredError,
    UrlAlreadyExistsError,
    get_http_err_content,
)


@dataclass
class RetryConfig:
    exceptions: Tuple[Type[Exception]]  # Exceptions tuple
    total_tries: int
    initial_wait: float
    backoff_factor: int


base_retry_config = RetryConfig(
    exceptions=(HTTPStatusError,), total_tries=3, initial_wait=0.5, backoff_factor=2
)


def retry(retry_config: RetryConfig):
    """
    calling the decorated function applying an exponential backoff.
    Args:
        exceptions: Exeption(s) that trigger a retry, can be a tuble
        total_tries: Total tries
        initial_wait: Time to first retry
        backoff_factor: Backoff multiplier 
        (e.g. value of 2 will double the delay each retry).
        logger: logger to be used, if none specified print
    """

    def retry_decorator(f):
        @wraps(f)
        def func_with_retries(*args, **kwargs):
            _tries, _delay = retry_config.total_tries + 1, retry_config.initial_wait
            while _tries > 1:
                try:
                    debug(f"{retry_config.total_tries + 2 - _tries}. try:")
                    return f(*args, **kwargs)
                except retry_config.exceptions as e:
                    _tries -= 1
                    print_args = args if args else "no args"
                    if _tries == 1:
                        msg = str(
                            f"Function: {f.__name__}\n"
                            f"""Failed despite best efforts after 
                            {retry_config.total_tries} tries.\n"""
                            f"args: {print_args}, kwargs: {kwargs}"
                        )
                        debug(msg)
                        raise
                    msg = str(
                        f"Function: {f.__name__}\n"
                        f"Exception: {e}\n"
                        f"""Retrying in {_delay} seconds!, 
                        args: {print_args}, kwargs: {kwargs}\n"""
                    )
                    debug(msg)
                    time.sleep(_delay)
                    _delay *= retry_config.backoff_factor

        return func_with_retries

    return retry_decorator


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
