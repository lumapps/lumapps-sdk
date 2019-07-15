# Standard Imports
from unittest.mock import ANY, Mock

# ThirdParty Imports
import asyncio


def fake_req_args(headers=ANY, data=ANY, params=ANY, json=ANY):
    req_args = {
        "headers": headers,
        "data": data,
        "params": params,
        "json": json,
        "ssl": ANY,
        "proxy": ANY,
    }
    return req_args


def fake_send_req_args(headers=ANY, data=ANY, params=ANY, json=ANY):
    req_args = {
        "headers": headers,
        "data": data,
        "params": params,
        "json": json,
        "ssl": ANY,
        "proxy": ANY,
        "files": ANY,
    }
    return req_args


def async_test(coro):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    def wrapper(*args, **kwargs):
        return asyncio.get_event_loop().run_until_complete(
            coro(*args, **kwargs)
        )

    return wrapper


def mock_request():
    response_mock = Mock(name="Response")
    data = {"data": {"test": True}, "headers": ANY, "status_code": 200}
    response_mock.return_value = data

    send_request = Mock(
        name="Request", side_effect=asyncio.coroutine(response_mock)
    )
    send_request.response = response_mock
    return send_request


def add_list_data_to_mock(mocked_request):
    mocked_request.response.side_effect = [
        {
            "data": {
                "cursor": "2689dadarr",
                "more": True,
                "items": [{"id": "10001"}, {"id": "10002"}],
            },
            "status_code": 200,
            "headers": {},
        },
        {
            "data": {
                "cursor": "",
                "more": False,
                "items": [{"id": "10001"}, {"id": "10004"}],
            },
            "status_code": 200,
            "headers": {},
        },
    ]
    return mocked_request
