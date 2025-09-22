import pytest

from src.api.endpoints.annotate.all.post.models.request import AllAnnotationPostInfo
from src.db.models.impl.flag.url_validated.enums import URLType
from tests.helpers.setup.final_review.core import setup_for_get_next_url_for_final_review


@pytest.mark.asyncio
async def test_annotate_all_post_batch_filtering(api_test_helper):
    """
    Batch filtering should also work when posting annotations
    """
    ath = api_test_helper
    adb_client = ath.adb_client()
    setup_info_1 =  await setup_for_get_next_url_for_final_review(
        db_data_creator=ath.db_data_creator, include_user_annotations=False
    )
    url_mapping_1 = setup_info_1.url_mapping
    setup_info_2 = await setup_for_get_next_url_for_final_review(
        db_data_creator=ath.db_data_creator, include_user_annotations=False
    )
    setup_info_3 = await setup_for_get_next_url_for_final_review(
        db_data_creator=ath.db_data_creator, include_user_annotations=False
    )
    url_mapping_3 = setup_info_3.url_mapping

    # Submit the first annotation, using the third batch id, and receive the third URL
    post_response_1 = await ath.request_validator.post_all_annotations_and_get_next(
        url_id=url_mapping_1.url_id,
        batch_id=setup_info_3.batch_id,
        all_annotations_post_info=AllAnnotationPostInfo(
            suggested_status=URLType.NOT_RELEVANT,
            location_ids=[],
            agency_ids=[]
        )
    )

    assert post_response_1.next_annotation.url_info.url_id == url_mapping_3.url_id
