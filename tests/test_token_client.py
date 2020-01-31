import lumapps.api.utils
import lumapps.api.client
import lumapps.api.token_client


def test_token_client_1(mocker):
    mocker.patch(
        "lumapps.api.client.ApiClient.get_call",
        return_value={"accessToken": "foo1", "expiresAt": "12345"},
    )
    cli = lumapps.api.token_client.TokenClient("11111", token="FOO")
    assert cli.customer_id == "11111"
    token, exp = cli.get_token_and_expiry("foo@bar.com")
    assert token == "foo1"
    assert exp == 12345


def test_token_client_2(mocker):
    mocker.patch(
        "lumapps.api.client.ApiClient.get_call",
        return_value={"accessToken": "foo1", "expiresAt": "12345"},
    )
    cli = lumapps.api.token_client.TokenClient("11111", token="FOO")
    getter = cli.get_token_getter("foo@bar.com")
    token, exp = getter()
    assert token == "foo1"
    assert exp == 12345
