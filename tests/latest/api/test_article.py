import pytest
from lumapps.latest.api.exceptions import ApiException
from lumapps.latest.api.article import ArticleApi
from lumapps.latest.entities.article import Article


@pytest.mark.vcr()
def test_get_article(client) -> None:
    # With
    api = ArticleApi(client)

    # When
    article = api.get_article("3efd23b6-1738-46d2-94a9-e55343e1bf1e")

    # Then
    assert isinstance(article, Article)


@pytest.mark.vcr()
def test_get_article_not_found(client) -> None:
    # With
    api = ArticleApi(client)

    # Then, when
    with pytest.raises(ApiException):
        api.get_article("3efd23b6-1738-46d2-94a9-000000000000")
