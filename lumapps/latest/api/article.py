from lumapps.latest.client import IClient
from lumapps.latest.entities import Article, EntityIdValue, EntityId

from .swagger.contribution_v1 import ContributionV1GW


class ArticleApi(object):

    def __init__(self, client: IClient) -> None:
        self.gateway = ContributionV1GW(client)

    def get_article(self, article_id: EntityIdValue) -> Article:
        model = self.gateway.get_article(EntityId(article_id).str)
        return Article(
            EntityId(model.id),
            EntityId(model.author.user_id),
            model.created_at,
            model.structured_content.title.translations,
            model.structured_content.intro.translations,
        )
