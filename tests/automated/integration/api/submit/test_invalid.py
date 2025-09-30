import pytest

from src.api.endpoints.submit.url.enums import URLSubmissionStatus
from src.api.endpoints.submit.url.models.request import URLSubmissionRequest
from src.api.endpoints.submit.url.models.response import URLSubmissionResponse
from tests.helpers.api_test_helper import APITestHelper


@pytest.mark.asyncio
async def test_invalid(api_test_helper: APITestHelper):
    response: URLSubmissionResponse = await api_test_helper.request_validator.submit_url(
        request=URLSubmissionRequest(
            url="invalid_url"
        )
    )
    assert response.status == URLSubmissionStatus.INVALID