import pytest

from src.api.endpoints.annotate.all.get.models.response import GetNextURLForAllAnnotationResponse
from src.db.dtos.url.mapping_.simple import SimpleURLMapping
from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.setup.final_review.core import setup_for_get_next_url_for_final_review
from tests.helpers.setup.final_review.model import FinalReviewSetupInfo


@pytest.mark.asyncio
async def test_offset(
    api_test_helper: APITestHelper,
):
    """
    Test that offset functionality works as expected when getting
    user annotations
    """

    ath = api_test_helper

    # Set up URLs
    setup_info_1: FinalReviewSetupInfo =  await setup_for_get_next_url_for_final_review(
        db_data_creator=ath.db_data_creator, include_user_annotations=True
    )
    url_mapping_1: SimpleURLMapping = setup_info_1.url_mapping
    setup_info_2: FinalReviewSetupInfo = await setup_for_get_next_url_for_final_review(
        db_data_creator=ath.db_data_creator, include_user_annotations=True
    )
    url_mapping_2: SimpleURLMapping = setup_info_2.url_mapping


    get_response_1: GetNextURLForAllAnnotationResponse = await ath.request_validator.get_next_url_for_all_annotations(
        offset=1
    )

    # Check that response is the second URL, rather than the first
    assert get_response_1.next_annotation.url_info.url_id == url_mapping_2.url_id

