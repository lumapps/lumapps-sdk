from lumapps.latest.api.exceptions import ApiException
from lumapps.latest.client import IClient, Request

from ..serialization import Serialization
from . import models


class ContributionV1GW(object):
    def __init__(self, client: IClient) -> None:
        self.client = client

    def get_article(self, article_id: str) -> models.Article:
        request = Request(
            method="GET",
            url=f"/articles/{article_id}",
        )
        response = self.client.request(request)
        if response.status_code == 200:
            return Serialization(models).deserialize(response.json, models.Article)
        else:
            raise ApiException(
                Serialization(models)
                .deserialize(response.json["errors"][0], models.Error)
                .detail,
            )
