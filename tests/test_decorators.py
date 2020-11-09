import httpx
import pytest
from pytest_httpx import HTTPXMock

from lumapps.api.decorators import (
    retry,
    RetryConfig, 
    base_retry_config, 
    none_on_http_codes,
    retry_on_http_codes,
    none_on_404,
    false_on_404,
    none_on_code_and_message,
    none_on_400_ALREADY_ARCHIVED,
    none_on_400_SUBSCRIPTION_ALREADY_EXISTS_OR_PINNED,
    raise_known_save_errors,
)
from lumapps.api.errors import UrlAlreadyExistsError, FeedsRequiredError

fake_url = "https://fakeurl.com"


### None on http codes

@none_on_http_codes(codes=(400,))
def fake_request_with_400_decorator():
    res = httpx.get(fake_url)
    res.raise_for_status()
    return res


def test_none_on_http_codes_1(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=400)
    res = fake_request_with_400_decorator()
 
    assert httpx_mock.get_requests()
    assert res is None


def test_none_on_http_codes_2(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=401)


    with pytest.raises(httpx.HTTPStatusError):
        fake_request_with_400_decorator()

    assert httpx_mock.get_requests()

## Retry on https codes

max_attempts = 3
@retry_on_http_codes(codes=(404,), max_attempts=max_attempts)
def fake_request_retry_on_http_codes():
    res = httpx.get(fake_url)
    res.raise_for_status()
    return res

def test_retry_on_http_codes(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=404)

    with pytest.raises(httpx.HTTPStatusError):
        fake_request_retry_on_http_codes()

    requests = httpx_mock.get_requests()
    assert requests
    assert len(requests) == max_attempts

# False on 404

@false_on_404
def fake_request_with_false_on_404_deco():
    res = httpx.get(fake_url)
    res.raise_for_status()
    return res


def test_false_on_404(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=404)


    res = fake_request_with_false_on_404_deco()

    assert httpx_mock.get_requests()
    assert res is False

## None on 404

@none_on_404
def fake_request_with_none_on_404_deco():
    res = httpx.get(fake_url)
    res.raise_for_status()
    return res



def test_none_on_404_1(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=404)

    res = fake_request_with_none_on_404_deco()

    assert httpx_mock.get_requests()
    assert res is None

def test_none_on_404_2(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=403)

    with pytest.raises(httpx.HTTPStatusError):
        fake_request_with_none_on_404_deco()

    assert httpx_mock.get_requests()

## None on code and message

@none_on_code_and_message(403, "message")
def fake_request_with_none_on_code_and_message():
    res = httpx.get(fake_url)
    res.raise_for_status()
    return res


def test_none_on_code_and_message_1(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=403, data=b"message")

    res = fake_request_with_none_on_code_and_message()

    assert httpx_mock.get_requests()
    assert res is None

def test_none_on_code_and_message_2(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=402, data=b"message")

    with pytest.raises(httpx.HTTPStatusError):
        fake_request_with_none_on_code_and_message()

    assert httpx_mock.get_requests()

def test_none_on_code_and_message_3(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=403, data=b"pas le mot dedans")

    with pytest.raises(httpx.HTTPStatusError):
        fake_request_with_none_on_code_and_message()

    assert httpx_mock.get_requests()

## none on 400 already archived

@none_on_400_ALREADY_ARCHIVED
def fake_request_with_none_on_400_ALREADY_ARCHIVED():
    res = httpx.get(fake_url)
    res.raise_for_status()
    return res


def test_none_on_400_ALREADY_ARCHIVED_1(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=400, data=b"ALREADY_ARCHIVED")

    res = fake_request_with_none_on_400_ALREADY_ARCHIVED()

    assert httpx_mock.get_requests()
    assert res is None

def test_none_on_400_ALREADY_ARCHIVED_2(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=401, data=b"ALREADY_ARCHIVED")

    with pytest.raises(httpx.HTTPStatusError):
        fake_request_with_none_on_400_ALREADY_ARCHIVED()

    assert httpx_mock.get_requests()

## none on 400 subscription already exists or pinned

@none_on_400_SUBSCRIPTION_ALREADY_EXISTS_OR_PINNED
def fake_request_with_none_on_400_SUBSCRIPTION_ALREADY_EXISTS_OR_PINNED():
    res = httpx.get(fake_url)
    res.raise_for_status()
    return res


def test_none_on_400_SUBSCRIPTION_ALREADY_EXISTS_OR_PINNED_1(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=400, data=b"SUBSCRIPTION_ALREADY_EXISTS")

    res = fake_request_with_none_on_400_SUBSCRIPTION_ALREADY_EXISTS_OR_PINNED()

    assert httpx_mock.get_requests()
    assert res is None


def test_none_on_400_SUBSCRIPTION_ALREADY_EXISTS_OR_PINNED_2(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=400, data=b"Already pinned")

    res = fake_request_with_none_on_400_SUBSCRIPTION_ALREADY_EXISTS_OR_PINNED()

    assert httpx_mock.get_requests()
    assert res is None

def test_none_on_400_SUBSCRIPTION_ALREADY_EXISTS_OR_PINNED_3(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=401, data=b"Already pinned")

    with pytest.raises(httpx.HTTPStatusError):
        fake_request_with_none_on_400_SUBSCRIPTION_ALREADY_EXISTS_OR_PINNED()

    assert httpx_mock.get_requests()


## raise known save errors

@raise_known_save_errors
def fake_request_with_raise_known_save_errors():
    res = httpx.get(fake_url)
    res.raise_for_status()
    return res


def test_raise_known_save_errors_1(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=400, data=b"URL_ALREADY_EXISTS")

    with pytest.raises(UrlAlreadyExistsError):
        fake_request_with_raise_known_save_errors()

    assert httpx_mock.get_requests()


def test_raise_known_save_errors_2(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=400, data=b"Feeds are required")

    with pytest.raises(FeedsRequiredError):
        fake_request_with_raise_known_save_errors()

    assert httpx_mock.get_requests()

@retry(base_retry_config)
def fake_request_with_base_retry():
    res = httpx.get(fake_url)
    res.raise_for_status()
    return res

def test_retry_with_base_config(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=400)

    with pytest.raises(Exception):
        fake_request_with_base_retry()
    
    requests_made = httpx_mock.get_requests()
    assert requests_made and len(requests_made) == base_retry_config.total_tries

config = RetryConfig(
    (Exception,),
    2,
    0.5,
    2
)
@retry(config)
def fake_request_with_base_retry():
    res = httpx.get(fake_url)
    res.raise_for_status()
    return res

def test_retry_with_base_config(httpx_mock: HTTPXMock):
    httpx_mock.add_response(status_code=400)

    with pytest.raises(Exception):
        fake_request_with_base_retry()
    
    requests_made = httpx_mock.get_requests()
    assert requests_made and len(requests_made) == 2
    

