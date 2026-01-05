import pytest

from src.api.endpoints.annotate.all.post.models.agency import AnnotationPostAgencyInfo
from src.api.endpoints.annotate.all.post.models.location import AnnotationPostLocationInfo
from src.api.endpoints.annotate.all.post.models.name import AnnotationPostNameInfo
from src.api.endpoints.annotate.all.post.models.request import AllAnnotationPostInfo
from src.core.enums import RecordType
from src.db.models.impl.annotation.url_type.user.sqlalchemy import AnnotationURLTypeUser
from src.db.models.impl.flag.url_validated.enums import URLType
from tests.helpers.api_test_helper import APITestHelper
from tests.helpers.data_creator.models.creation_info.us_state import USStateCreationInfo
from tests.helpers.setup.final_review.core import setup_for_get_next_url_for_final_review


@pytest.mark.asyncio
async def test_post_annotate_return_no_annotation(
    api_test_helper: APITestHelper,
    pennsylvania: USStateCreationInfo,
    test_agency_id: int
):
    """
    If the `return_new_annotation` query arg is false,
    do not return a new annotation.
    """
    ath = api_test_helper
    adb_client = ath.adb_client()

    # Set up URLs
    setup_info_1 =  await setup_for_get_next_url_for_final_review(
        db_data_creator=ath.db_data_creator, include_user_annotations=True
    )
    url_mapping_1 = setup_info_1.url_mapping
    setup_info_2 = await setup_for_get_next_url_for_final_review(
        db_data_creator=ath.db_data_creator, include_user_annotations=True
    )
    url_mapping_2 = setup_info_2.url_mapping

    post_response_1 = await ath.request_validator.post_all_annotations(
        url_id=url_mapping_1.url_id,
        all_annotations_post_info=AllAnnotationPostInfo(
            suggested_status=URLType.DATA_SOURCE,
            record_type=RecordType.ACCIDENT_REPORTS,
            agency_info=AnnotationPostAgencyInfo(agency_ids=[test_agency_id]),
            location_info=AnnotationPostLocationInfo(
                location_ids=[
                    pennsylvania.location_id,
                ]
            ),
            name_info=AnnotationPostNameInfo(
                new_name="New Name"
            )
        ),
        get_next_url=False
    )
    assert post_response_1.next_annotation is None

    # Check annotation still posted to DB
    # Check URL Type Suggestions
    all_relevance_suggestions: list[AnnotationURLTypeUser] = await adb_client.get_all(AnnotationURLTypeUser)
    assert len(all_relevance_suggestions) == 3
    suggested_types: set[URLType] = {sugg.type for sugg in all_relevance_suggestions}
    assert suggested_types == {URLType.DATA_SOURCE, URLType.NOT_RELEVANT}

