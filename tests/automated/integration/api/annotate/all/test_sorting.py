import pytest

from src.db.models.impl.url.core.enums import URLSource
from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.setup.final_review.core import setup_for_get_next_url_for_final_review
from tests.helpers.setup.final_review.model import FinalReviewSetupInfo


@pytest.mark.asyncio
async def test_annotate_sorting(
    api_test_helper: APITestHelper,

):
    """
    Test that annotations are prioritized in the following order:
    - Any manual submissions are prioritized first
    - Then prioritize by number of annotations descending
    - Then prioritize by URL ID ascending (e.g. least recently created)
    """
    ath = api_test_helper

    # First URL created should be prioritized in absence of any other factors
    setup_info_first_annotation: FinalReviewSetupInfo = await setup_for_get_next_url_for_final_review(
        db_data_creator=ath.db_data_creator,
        include_user_annotations=False
    )
    get_response_1 = await ath.request_validator.get_next_url_for_all_annotations()
    assert get_response_1.next_annotation is not None
    assert get_response_1.next_annotation.url_info.url_id == setup_info_first_annotation.url_mapping.url_id

    # ...But higher annotation count should take precedence over least recently created
    setup_info_high_annotations: FinalReviewSetupInfo = await setup_for_get_next_url_for_final_review(
        db_data_creator=ath.db_data_creator,
        include_user_annotations=True
    )
    get_response_2 = await ath.request_validator.get_next_url_for_all_annotations()
    assert get_response_2.next_annotation is not None
    assert get_response_2.next_annotation.url_info.url_id == setup_info_high_annotations.url_mapping.url_id

    # ...But manual submissions should take precedence over higher annotation count
    setup_info_manual_submission: FinalReviewSetupInfo = await setup_for_get_next_url_for_final_review(
        db_data_creator=ath.db_data_creator,
        source=URLSource.MANUAL,
        include_user_annotations=True
    )
    get_response_3 = await ath.request_validator.get_next_url_for_all_annotations()
    assert get_response_3.next_annotation is not None
    assert get_response_3.next_annotation.url_info.url_id == setup_info_manual_submission.url_mapping.url_id
