from lumapps.latest.client import ApplicationClient, Application, Request, InvalidLogin
from oauthlib.oauth2 import TokenExpiredError
from pytest import raises


def test_request(requests_mock):
    # Given
    token_mock = requests_mock.post(
        "https://mock/v2/organizations/123/application-token",
        request_headers={"Authorization": "Basic Y2xpZW50OnNlY3JldA=="},
        json={"access_token": "123"},
    )
    call_mock = requests_mock.get(
        "https://mock/v2/organizations/123/test",
        request_headers={"Authorization": "Bearer 123"},
        json="response"
    )
    client = ApplicationClient(
        "https://mock", "123", Application(client_id="client", client_secret="secret")
    )

    # When
    response = client.request(Request(method="GET", url="/test"))

    # Then
    assert response.status_code == 200
    assert response.json == "response"
    assert token_mock.call_count == 1
    assert call_mock.call_count == 1


def test_request_token_expired(requests_mock):
    # Given
    token_mock = requests_mock.post(
        "https://mock/v2/organizations/123/application-token",
        [
            {"json": {"access_token": "123"}},
            {"json": {"access_token": "456"}},
        ]
    )
    call_token_expired_mock = requests_mock.get(
        "https://mock/v2/organizations/123/test",
        request_headers={"Authorization": "Bearer 123"},
        exc=TokenExpiredError
    )
    call_token_updated_mock = requests_mock.get(
        "https://mock/v2/organizations/123/test",
        request_headers={"Authorization": "Bearer 456"},
        json="response"
    )
    client = ApplicationClient(
        "https://mock", "123", Application(client_id="client", client_secret="secret")
    )

    # When
    response = client.request(Request(method="GET", url="/test"))

    # Then
    assert response.status_code == 200
    assert response.json == "response"
    assert token_mock.call_count == 2
    assert call_token_expired_mock.call_count == 1
    assert call_token_updated_mock.call_count == 1


def test_request_no_token(requests_mock):
    # Given
    token_mock = requests_mock.post(
        "https://mock/v2/organizations/123/application-token",
        status_code=400,
        json={"error": "invalid_request"},
    )
    client = ApplicationClient(
        "https://mock", "123", Application(client_id="client", client_secret="secret")
    )

    # When
    with raises(InvalidLogin):
        client.request(Request(method="GET", url="/test"))

    # Then
    assert token_mock.call_count == 1
