from lumapps.api import TokenClient


def test_token_client_1(mocker):
    mocker.patch(
        "lumapps.api.client.BaseClient.get_call",
        return_value={"accessToken": "foo1", "expiresAt": "12345"},
    )
    cli = TokenClient("11111", token="FOO")
    assert cli.customer_id == "11111"
    token, exp = cli._get_token_and_expiry("foo@bar.com")
    assert token == "foo1"
    assert exp == 12345


def test_token_client_2(mocker):
    mocker.patch(
        "lumapps.api.client.BaseClient.get_call",
        return_value={"accessToken": "foo1", "expiresAt": "12345"},
    )
    cli = TokenClient("11111", token="FOO")
    getter = cli.get_token_getter("foo@bar.com")
    token, exp = getter()
    assert token == "foo1"
    assert exp == 12345
