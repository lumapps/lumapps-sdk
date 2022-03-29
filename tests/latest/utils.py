import jwt
from typing import Any
import requests
from datetime import datetime, timedelta

from lumapps.latest.client import IClient, Request, Response


NOW = datetime.utcnow()
USER_ID = "42"
ORG_ID = "5663677907730432"
JWT = {
    "iss": "https://sdk-tests",
    "iat": NOW,
    "exp": NOW + timedelta(seconds=60),
    "sub": USER_ID,
    "organizationId": ORG_ID,
    "email": "user@test.com",
}

# To record / update cassettes, override those two constants,
# and run `make test pytest_args="--record-mode=new_episodes"`.
# (change also the cell-url in the cassettes themself, match_request_on does not work atm)
TOKEN = jwt.encode(
  JWT, "secret", headers={"kid": "sdk-tests-key"}, algorithm="HS256"
)
CELL_URL = "https://cell-url"


class DirectClient(IClient):
    def __init__(
        self,
        cell_url: str = CELL_URL,
        token: str = TOKEN,
    ) -> None:
        org_id = jwt.decode(token, options={"verify_signature": False})["organizationId"]
        self._org_url = f"{cell_url}/v2/organizations/{org_id}"
        self._token = token

    def request(self, request: Request, **_: Any) -> Response:
        response = requests.request(
            request.method,
            f"{self._org_url}/{request.url.lstrip('/')}",
            params=request.params,
            headers={
                **request.headers,
                "Authorization": f"Bearer {self._token}",
                "User-Agent": "lumapps-sdk-tests",
            },
            json=request.json,
        )
        return Response(
            status_code=response.status_code,
            headers=dict(response.headers),
            json=response.json() if response.text else None,
        )
