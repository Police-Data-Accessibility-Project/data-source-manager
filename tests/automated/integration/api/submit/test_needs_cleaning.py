import pytest

from src.api.endpoints.submit.url.enums import URLSubmissionStatus
from src.api.endpoints.submit.url.models.request import URLSubmissionRequest
from src.api.endpoints.submit.url.models.response import URLSubmissionResponse
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.link.user_suggestion_not_found.users_submitted_url.sqlalchemy import LinkUserSubmittedURL
from src.db.models.impl.url.core.sqlalchemy import URL
from tests.helpers.api_test_helper import APITestHelper


@pytest.mark.asyncio
async def test_needs_cleaning(
    api_test_helper: APITestHelper,
    adb_client_test: AsyncDatabaseClient
):
    response: URLSubmissionResponse = await api_test_helper.request_validator.submit_url(
        request=URLSubmissionRequest(
            url="www.example.com#fdragment"
        )
    )

    assert response.status == URLSubmissionStatus.ACCEPTED_WITH_CLEANING
    assert response.url_id is not None
    url_id: int = response.url_id

    adb_client: AsyncDatabaseClient = adb_client_test
    urls: list[URL] = await adb_client.get_all(URL)
    assert len(urls) == 1
    url: URL = urls[0]
    assert url.id == url_id
    assert url.url == "www.example.com"

    links: list[LinkUserSubmittedURL] = await adb_client.get_all(LinkUserSubmittedURL)
    assert len(links) == 1
    link: LinkUserSubmittedURL = links[0]
    assert link.url_id == url_id