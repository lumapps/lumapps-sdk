from _pytest.outcomes import Skipped
import httpx
import pytest
import jwt 
import base64
import json
import datetime 
import calendar

from lumapps.api.errors import (
    LumAppsJwtTokenExpiredError,
    LumAppsJwtInvalidClaimError,
    LumAppsJwtCustomError,
    LumAppsJwtHeaderError
)

from lumapps.api.lumapps_jwt import LumappsJWT


TOKEN = b"eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6InN5bi1rZXktdjAifQ.eyJpc3MiOiJodHRwczovL2xvZ2luLmx1bWFwcHMuY29tL3YxIiwiaWF0IjoxNjIxODYwMzMwLCJleHAiOjE2MjE4NjM5MzAsImF1ZCI6Imh0dHBzOi8vbHVtc2l0ZXMuYXBwc3BvdC5jb20vX2FoL2FwaS9sdW1zaXRlcyIsInN1YiI6IjY3NTM1NTI3ODM3Njk2MDAiLCJvcmdhbml6YXRpb25JZCI6IjU3Njk5Mjg4NTg2NjQ5NjAiLCJlbWFpbCI6ImFpQGx1bWFwcHMuY29tIn0.XOgTJNt5h0eG65UYxRLNMfpcvGE-TBxftNATjfHoL8JoNovB_McP96kgvka2FZN6u89RcrT3enHqOUS-vMpeRvmzjJ6UruUDJaHB4km2blK2nO6zZvpnmbFnQBLj856vendqbesni_a2CHLATbc44aHs6fdEHMREjBsbmTr1QU6KD6IBBtMPsqvvwI3I7ggS4FeReRlmCV5rd8ZgwE0Nft1_3aoLuqUUtNw9cdxm87swG-ezPQugt2XVfpPo-t4NLjZiRpnSfu1Oqd9jlQWEFKiIUPJnTslKNIzE9pXMaJDTXfu26aSLttEm_qiJB9rhqRevBxEm-Zj5AVQ6OmlrLUSCV0hpokZpKYkAaOgwjnxggbujxy9jn2ItaNblb_sL0mz-S7VM3CEbpAwCqIhAVWOQXpReAyjECKfmjU5jRdjtIEXy0rEhdI0R8UwTYWbukGZyLplI434GDZAf-MvqjhxZdCTGinESCPJJeDvDhI_hSEn7QY08QdGdoLGIl4wQKu3JPKQQ2d8zSruQvLETFJReWrCyooJMMm6Rr0tTxVPL4I7nqsYlYAMBY3KkhDALtQF4kTcq1tpHupojv7hxzOGZpBNSlNLhuqwtXQwUkXo96anTITA6h2An_S2nRckaKpTWUoGtJxLxjjLoLuFJjzW8XJqOYtbW_fH0HX7qCg4"


def utcnow():
    """Returns the current UTC datetime.
    Returns:
        datetime: The current time in UTC.
    """
    return datetime.datetime.utcnow()


def datetime_to_secs(value):
    """Convert a datetime object to the number of seconds since the UNIX epoch.
    Args:
        value (datetime): The datetime to convert.
    Returns:
        int: The number of seconds since the UNIX epoch.
    """
    return calendar.timegm(value.utctimetuple())


# @pytest.fixture
# def token_factory(signer, claims=None):
#     now = datetime_to_secs(utcnow())
#     payload = {
#         "iat": now,
#         "exp": now + 3600,
#         "aud": "https://lumsites.appspot.com/_ah/api/lumsites",
#         "email": "harry@example.com",
#     }
#     payload.update(claims or {})
#     return jwt.encode( {'data': payload} , signer , algorithm = "RS256", headers= {"kid": "syn-key-v0"})

def test_decode_valid():
    with pytest.raises(LumAppsJwtTokenExpiredError) as exinfo:
        payload = LumappsJWT().decode(TOKEN)
        assert str(exinfo.value) == "Token is expired."
        assert payload["aud"] == "https://lumsites.appspot.com/_ah/api/lumsites"
        assert payload["email"] == "ai@lumapps.com"

        
# def test_decode_token_expired(token_factory):
#     token = token_factory(
#         claims = {
#             "exp": datetime_to_secs(utcnow()- datetime.timedelta(hours=2))
#         }
#     )
#     with pytest.raises(LumAppsJwtTokenExpiredError) as excinfo:
#         LumappsJWT.decode(token)
#         assert str(excinfo.value) == "Token is expired."

# def test_decode_invalid_claim():
#     token = jwt.encode(RSA_PRIVATE, {"test": "value"})
#     with pytest.raises(LumAppsJwtInvalidClaimError) as excinfo:
#         LumappsJWT.decode(token)
#         assert str(excinfo.value) == "Invalid claims."
