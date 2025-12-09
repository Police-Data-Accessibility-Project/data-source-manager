import pytest

from src.api.endpoints.submit.url.enums import URLSubmissionStatus
from src.api.endpoints.submit.url.models.request import URLSubmissionRequest
from src.api.endpoints.submit.url.models.response import URLSubmissionResponse
from src.db.dtos.url.mapping_.simple import SimpleURLMapping
from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_duplicate(
    api_test_helper: APITestHelper,
    db_data_creator: DBDataCreator
):
    url_mapping: SimpleURLMapping = (await db_data_creator.create_urls(count=1))[0]

    response: URLSubmissionResponse = await api_test_helper.request_validator.submit_url(
        request=URLSubmissionRequest(
            url=url_mapping.url
        )
    )
    assert response.status == URLSubmissionStatus.DATABASE_DUPLICATE
    assert response.url_id is None