from dataclasses import dataclass
from typing import Any, Callable

from oauthlib.oauth2 import BackendApplicationClient, OAuth2Error, TokenExpiredError
from requests_oauthlib import OAuth2Session

from .base import IClient, Request, Response
from .exceptions import InvalidLogin


@dataclass(frozen=True)
class Application:
    client_id: str
    client_secret: str


def retry_on_expired_token(func: Callable[..., Response]) -> Callable[..., Response]:
    def inner(client: "ApplicationClient", request: Request, **kwargs: Any) -> Response:
        try:
            return func(client, request, **kwargs)
        except TokenExpiredError:
            client.fetch_token()
            return func(client, request, **kwargs)

    return inner


class ApplicationClient(IClient):
    def __init__(
        self, base_url: str, organization_id: str, application: Application
    ) -> None:
        """
        Args:
            base_url: The API base url, i.e your Haussmann cell.
            e.g: https://XX-cell-YYY.api.lumapps.com
            organization_id: The ID of the given customer / organization.
            application: A LumApps application of the same customer.
        """
        self.base_url = base_url.rstrip("/")
        self.organization_id = organization_id
        self.application = application
        self.session = OAuth2Session(
            client=BackendApplicationClient(
                client_id=application.client_id,
                scope=None,
            )
        )
        self.organization_url = (
            f"{self.base_url}/v2/organizations/{self.organization_id}"
        )

    @retry_on_expired_token
    def request(self, request: Request, **_: Any) -> Response:
        if not self.session.token:
            # Ensure token in request
            self.fetch_token()
        response = self.session.request(
            request.method,
            f"{self.organization_url}/{request.url.lstrip('/')}",
            params=request.params,
            headers={
                **request.headers,
                "User-Agent": "lumapps-sdk",
                "x-lumapps-analytics": "off",
            },
            json=request.json,
        )
        return Response(
            status_code=response.status_code,
            headers=dict(response.headers),
            json=response.json() if response.text else None,
        )

    def fetch_token(self) -> None:
        try:
            self.session.fetch_token(
                f"{self.organization_url}/application-token",
                client_secret=self.application.client_secret,
            )
        except OAuth2Error as err:
            raise InvalidLogin("Could not fetch token from application") from err
