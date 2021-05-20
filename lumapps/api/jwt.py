import jwt
import requests
import requests_cache

from . import DEFAULT_KEYS
from .exceptions.exception import InvalidUsage

JWKS_URL = {
    "dot-lumapps-staging.appspot.com": "https://login.stag.lumapps.com/v1/jwks",
    "sites-staging.lumapps.com": "https://login.stag.lumapps.com/v1/jwks",
    "sites-analytics.lumapps.com": "https://login.dev.lumapps.com/v1/jwks",
    "sites-ba.lumapps.com": "https://login.dev.lumapps.com/v1/jwks",
    "sites-cms.lumapps.com": "https://login.dev.lumapps.com/v1/jwks",
    "sites-core.lumapps.com": "https://login.dev.lumapps.com/v1/jwks",
    "sites-sa.lumapps.com": "https://login.dev.lumapps.com/v1/jwks",
    "sites-search.lumapps.com": "https://login.dev.lumapps.com/v1/jwks",
    "sites-social.lumapps.com": "https://login.dev.lumapps.com/v1/jwks",
    "sites-dev.lumapps.com": "https://login.dev.lumapps.com/v1/jwks",
    "sites-sandbox.lumapps.com": "https://login-sandbox.dev.lumapps.com/v1/jwks",
    "sites-beta.lumapps.com": "https://login.beta.lumapps.com/v1/jwks",
    "sites-beta.eu.lumapps.com": "https://login.beta.lumapps.com/v1/jwks",
}


class LumappsJWT(object):
    def jwt_verification(self, lumapps_url="https://sites.lumapps.com"):
        jwks_url = None
        for key in JWKS_URL.keys():
            if key in lumapps_url:
                jwks_url = JWKS_URL[key]

            if not jwks_url:
                jwks_url = "https://login.lumapps.com/v1/jwks"

            try:
                requests_cache.configure()
                r = requests.get(jwks_url)
                if r.status_code == 200:
                    self._key = r.json()
                else:
                    self._key = DEFAULT_KEYS
            except Exception:
                self._key = DEFAULT_KEYS

    def decode(self, token):
        unverified_header = jwt.get_unverified_header(token)
        for jwk in self._key["keys"]:
            if jwk["kid"] == unverified_header["kid"]:
                rsa_key = {"typ": jwk["typ"], "alg": jwk["alg"], "kid": jwk["kid"]}
        if rsa_key:
            try:
                return jwt.decode(
                    token, rsa_key, algorithms=["RS256"], options={"verify_aud": False},
                )
            except jwt.ExpiredSignatureError:
                raise InvalidUsage(
                    {"code": "token_expired", "description": "token is expired"}, 401
                )
            except jwt.JWTClaimsError:
                raise InvalidUsage(
                    {
                        "code": "invalid_claims",
                        "description": "incorrect claims,"
                        "please check the audience and issuer",
                    },
                    401,
                )
            except Exception:
                raise InvalidUsage(
                    {
                        "code": "invalid_header",
                        "description": "Unable to parse authentication" " token.",
                    },
                    401,
                )

        raise InvalidUsage(
            {"code": "invalid_header", "description": "Unable to find appropriate key"},
            401,
        )
