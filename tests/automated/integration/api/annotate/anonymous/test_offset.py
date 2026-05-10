import pytest

from src.api.endpoints.annotate.anonymous.get.response import GetNextURLForAnonymousAnnotationResponse
from src.db.dtos.url.mapping_.simple import SimpleURLMapping
from tests.automated.integration.api.annotate.anonymous.helper import get_next_url_for_anonymous_annotation
from tests.helpers.setup.final_review.core import setup_for_get_next_url_for_final_review
from tests.helpers.setup.final_review.model import FinalReviewSetupInfo


@pytest.mark.asyncio
async def test_offset(
    api_test_helper,
):

    ath = api_test_helper
    rv = ath.request_validator

    # Set up URLs
    setup_info_1 =  await setup_for_get_next_url_for_final_review(
        db_data_creator=ath.db_data_creator, include_user_annotations=True
    )
    url_mapping_1: SimpleURLMapping = setup_info_1.url_mapping
    setup_info_2: FinalReviewSetupInfo = await setup_for_get_next_url_for_final_review(
        db_data_creator=ath.db_data_creator, include_user_annotations=True
    )
    url_mapping_2: SimpleURLMapping = setup_info_2.url_mapping

    get_response_1: GetNextURLForAnonymousAnnotationResponse = await get_next_url_for_anonymous_annotation(
        rv,
        offset=1
    )

    # Check URL is second URL and not first
    assert get_response_1.next_annotation.url_info.url_id == url_mapping_1.url_id



