from lumapps.latest.client import IClient
from lumapps.latest.entities.article import Article

from .swagger.contribution_v1 import ContributionV1GW


class ArticleApi:
    def __init__(self, client: IClient) -> None:
        self.gateway = ContributionV1GW(client)

    def get_article(self, article_id: str) -> Article:
        model = self.gateway.get_article(article_id)
        return Article(
            model.id,
            model.author.user_id,
            model.created_at,
            model.structured_content.title.translations,
            model.structured_content.intro.translations,
        )
