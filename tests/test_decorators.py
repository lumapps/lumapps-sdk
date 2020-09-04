import httpx
import respx
import pytest

from lumapps.api.decorators import (
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


@respx.mock
def test_none_on_http_codes_1():
    request = respx.get(fake_url, status_code=400)
    res = fake_request_with_400_decorator()

    assert request.called
    assert res is None


@respx.mock
def test_none_on_http_codes_2():
    request = respx.get(fake_url, status_code=401)

    with pytest.raises(httpx.HTTPStatusError):
        fake_request_with_400_decorator()

    assert request.called

## Retry on https codes

max_attempts = 3
@retry_on_http_codes(codes=(404,), max_attempts=max_attempts)
def fake_request_retry_on_http_codes():
    res = httpx.get(fake_url)
    res.raise_for_status()
    return res

@respx.mock
def test_retry_on_http_codes():
    request = respx.get(fake_url, status_code=404)

    with pytest.raises(httpx.HTTPStatusError):
        fake_request_retry_on_http_codes()

    assert request.called
    assert request.call_count == max_attempts

## False on 404

@false_on_404
def fake_request_with_false_on_404_deco():
    res = httpx.get(fake_url)
    res.raise_for_status()
    return res


@respx.mock
def test_false_on_404():
    request = respx.get(fake_url, status_code=404)

    res = fake_request_with_false_on_404_deco()

    assert request.called
    assert res is False

## None on 404

@none_on_404
def fake_request_with_none_on_404_deco():
    res = httpx.get(fake_url)
    res.raise_for_status()
    return res


@respx.mock
def test_none_on_404_1():
    request = respx.get(fake_url, status_code=404)

    res = fake_request_with_none_on_404_deco()

    assert request.called
    assert res is None

@respx.mock
def test_none_on_404_2():
    request = respx.get(fake_url, status_code=403)

    with pytest.raises(httpx.HTTPStatusError):
        fake_request_with_none_on_404_deco()

    assert request.called

## None on code and message

@none_on_code_and_message(403, "message")
def fake_request_with_none_on_code_and_message():
    res = httpx.get(fake_url)
    res.raise_for_status()
    return res


@respx.mock
def test_none_on_code_and_message_1():
    request = respx.get(fake_url, status_code=403, content=b"message")

    res = fake_request_with_none_on_code_and_message()

    assert request.called
    assert res is None

@respx.mock
def test_none_on_code_and_message_2():
    request = respx.get(fake_url, status_code=402, content=b"message")

    with pytest.raises(httpx.HTTPStatusError):
        fake_request_with_none_on_code_and_message()

    assert request.called

@respx.mock
def test_none_on_code_and_message83():
    request = respx.get(fake_url, status_code=403, content=b"pas essage")

    with pytest.raises(httpx.HTTPStatusError):
        fake_request_with_none_on_code_and_message()

    assert request.called

## none on 400 already archived

@none_on_400_ALREADY_ARCHIVED
def fake_request_with_none_on_400_ALREADY_ARCHIVED():
    res = httpx.get(fake_url)
    res.raise_for_status()
    return res


@respx.mock
def test_none_on_400_ALREADY_ARCHIVED_1():
    request = respx.get(fake_url, status_code=400, content=b"ALREADY_ARCHIVED")

    res = fake_request_with_none_on_400_ALREADY_ARCHIVED()

    assert request.called
    assert res is None

@respx.mock
def test_none_on_400_ALREADY_ARCHIVED_2():
    request = respx.get(fake_url, status_code=401, content=b"ALREADY_ARCHIVED")

    with pytest.raises(httpx.HTTPStatusError):
        fake_request_with_none_on_400_ALREADY_ARCHIVED()

    assert request.called

## none on 400 subscription already exists or pinned

@none_on_400_SUBSCRIPTION_ALREADY_EXISTS_OR_PINNED
def fake_request_with_none_on_400_SUBSCRIPTION_ALREADY_EXISTS_OR_PINNED():
    res = httpx.get(fake_url)
    res.raise_for_status()
    return res


@respx.mock
def test_none_on_400_SUBSCRIPTION_ALREADY_EXISTS_OR_PINNED_1():
    request = respx.get(
        fake_url, status_code=400, content=b"SUBSCRIPTION_ALREADY_EXISTS"
    )

    res = fake_request_with_none_on_400_SUBSCRIPTION_ALREADY_EXISTS_OR_PINNED()

    assert request.called
    assert res is None


@respx.mock
def test_none_on_400_SUBSCRIPTION_ALREADY_EXISTS_OR_PINNED_2():
    request = respx.get(fake_url, status_code=400, content=b"Already pinned")

    res = fake_request_with_none_on_400_SUBSCRIPTION_ALREADY_EXISTS_OR_PINNED()

    assert request.called
    assert res is None

@respx.mock
def test_none_on_400_SUBSCRIPTION_ALREADY_EXISTS_OR_PINNED_3():
    request = respx.get(fake_url, status_code=401, content=b"Already pinned")

    with pytest.raises(httpx.HTTPStatusError):
        fake_request_with_none_on_400_SUBSCRIPTION_ALREADY_EXISTS_OR_PINNED()

    assert request.called


## raise known save errors

@raise_known_save_errors
def fake_request_with_raise_known_save_errors():
    res = httpx.get(fake_url)
    res.raise_for_status()
    return res


@respx.mock
def test_raise_known_save_errors_1():
    request = respx.get(fake_url, status_code=400, content=b"URL_ALREADY_EXISTS")

    with pytest.raises(UrlAlreadyExistsError):
        fake_request_with_raise_known_save_errors()

    assert request.called


@respx.mock
def test_raise_known_save_errors_2():
    request = respx.get(fake_url, status_code=400, content=b"Feeds are required")

    with pytest.raises(FeedsRequiredError):
        fake_request_with_raise_known_save_errors()

    assert request.called
