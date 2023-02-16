from pytest import fixture

from lumapps.api import LumAppsClient
from lumapps.api.client import chunks


def test_chunks():
    liste = [2, 2, 3, 3]
    ck = chunks(liste, 2)
    assert next(ck) == [2, 2]
    assert next(ck) == [3, 3]


@fixture()
def cli():
    c = LumAppsClient("a", "b", token="FAKE")
    return c


def test_get_available_slug(mocker, cli: LumAppsClient):
    def dummy_get_content_by_slug(_, desired_slug, fields="id"):
        nonlocal count
        count += 1
        if count <= 10:
            return True
        return None

    mocker.patch(
        "lumapps.api.client.LumAppsClient.get_content_by_slug",
        dummy_get_content_by_slug,
    )
    count = 0
    slug = "foo-slug"
    new_slug = cli.get_available_slug(slug)
    assert new_slug == slug + "-10"
    count = 0
    slug = "first-project-items-are-due-1-goals-and-deliverables-2-project-members-3-due-dates-if-you-need"
    new_slug = cli.get_available_slug(slug)
    assert new_slug == slug + "-10"


def test_custom_headers():
    headers = {"my-header": "on"}
    cli = LumAppsClient("a", "b", token="FAKE", extra_http_headers=headers)
    assert "my-header" in cli.client.headers


def test_custom_headers_for_new_client(mocker):
    def dummy_get_call(*args, **kwargs):
        return {"accessToken": "1"}
    mocker.patch(
        "lumapps.api.base_client.BaseClient.get_call",
        dummy_get_call,
    )

    headers = {"my-header": "on"}
    cli = LumAppsClient("a", "b", token="FAKE", extra_http_headers=headers)
    new_as = cli.get_new_client_as("user_email")
    assert "my-header" in new_as.client.headers
