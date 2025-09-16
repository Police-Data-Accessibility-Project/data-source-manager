import pytest

from src.api.endpoints.annotate.all.post.models.request import AllAnnotationPostInfo
from src.core.enums import SuggestedStatus, RecordType
from src.core.exceptions import FailedValidationException
from tests.helpers.setup.final_review.core import setup_for_get_next_url_for_final_review


@pytest.mark.asyncio
async def test_annotate_all_validation_error(api_test_helper):
    """
    Validation errors in the PostInfo DTO should result in a 400 BAD REQUEST response
    """
    ath = api_test_helper
    setup_info_1 = await setup_for_get_next_url_for_final_review(
        db_data_creator=ath.db_data_creator, include_user_annotations=False
    )
    url_mapping_1 = setup_info_1.url_mapping

    with pytest.raises(FailedValidationException) as e:
        response = await ath.request_validator.post_all_annotations_and_get_next(
            url_id=url_mapping_1.url_id,
            all_annotations_post_info=AllAnnotationPostInfo(
                suggested_status=SuggestedStatus.NOT_RELEVANT,
                record_type=RecordType.ACCIDENT_REPORTS,
                location_ids=[]
            )
        )
