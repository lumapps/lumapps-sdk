import json
from typing import Any, Dict

import httpx
import jwt

from lumapps.api.decorators import retry_on_http_status_error
from lumapps.api.errors import (
    LumAppsJWTClaimsError,
    LumAppsJwtCustomError,
    LumAppsJwtHeaderError,
    LumAppsJwtInvalidClaimError,
    LumAppsJwtTokenExpiredError,
)

JWKS_URL = {
    "dot-lumapps-analytics.appspot.com": "https://login.dev.lumapps.com/v1/jwks",
    "dot-lumapps-ba.appspot.com": "https://login.dev.lumapps.com/v1/jwks",
    "dot-lumapps-cms.appspot.com": "https://login.dev.lumapps.com/v1/jwks",
    "dot-lumapps-core.appspot.com": "https://login.dev.lumapps.com/v1/jwks",
    "dot-lumapps-sa.appspot.com": "https://login.dev.lumapps.com/v1/jwks",
    "dot-lumapps-search.appspot.com": "https://login.dev.lumapps.com/v1/jwks",
    "dot-lumapps-social.appspot.com": "https://login.dev.lumapps.com/v1/jwks",
    "dot-lumapps-dev.appspot.com": "https://login.dev.lumapps.com/v1/jwks",
    "dot-lumapps-sandbox.appspot.com": "https://login-sandbox.dev.lumapps.com/v1/jwks",
    "dot-lumapps-beta.appspot.com": "https://login.beta.lumapps.com/v1/jwks",
    "dot-lumapps-beta.eu.appspot.com": "https://login.beta.lumapps.com/v1/jwks",
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
    """
    This module aims to fetch and decode JWT token for lumapps APIs
    it's supposed to return a decoded payload
    """

    def __init__(self, lumapps_url="https://sites.lumapps.com"):
        self.jwks_url = None
        self.lumapps_url = lumapps_url
        self._key = None

        self.get_public_keys()

    @retry_on_http_status_error()
    def get_public_keys(self):
        """
            Get the public keys used by lumapps in order to be able to
            to decode the token later on
        """

        jwks_url = "https://login.lumapps.com/v1/jwks"

        for key in JWKS_URL.keys():
            if key in self.lumapps_url:
                jwks_url = JWKS_URL[key]
                break

        r = httpx.get(jwks_url)
        if r.status_code == httpx.codes.OK:
            self._key = r.json()

    def decode(self, token: str) -> Dict[str, Any]:
        """
            Args:
                token: The jwt token to decode
            
            Returns:
                the decoded token
        """
        public_keys = {}
        unverified_header = jwt.get_unverified_header(token)
        for jwk in self._key["keys"]:
            if jwk["kid"] == unverified_header["kid"]:
                kid = jwk["kid"]
                public_keys[kid] = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
                rsa_key = public_keys[kid]
                if rsa_key:
                    try:
                        return jwt.decode(
                            token,
                            rsa_key,
                            algorithms=["RS256"],
                            options={"verify_aud": False},
                        )
                    except jwt.ExpiredSignatureError:
                        raise LumAppsJwtTokenExpiredError("Token is expired.")
                    except LumAppsJWTClaimsError:
                        raise LumAppsJwtInvalidClaimError(
                            "Incorrect claims, please check the audience and issuer."
                        )
                    except Exception as e:
                        raise LumAppsJwtCustomError(e)
        raise LumAppsJwtHeaderError("Unable to find appropriate key.")
