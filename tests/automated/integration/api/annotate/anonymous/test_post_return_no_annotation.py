import pytest

from src.api.endpoints.annotate.all.post.models.agency import AnnotationPostAgencyInfo
from src.api.endpoints.annotate.all.post.models.location import AnnotationPostLocationInfo
from src.api.endpoints.annotate.all.post.models.name import AnnotationPostNameInfo
from src.api.endpoints.annotate.all.post.models.request import AllAnnotationPostInfo
from src.api.endpoints.annotate.anonymous.get.response import GetNextURLForAnonymousAnnotationResponse
from src.core.enums import RecordType
from src.db.dtos.url.mapping_.simple import SimpleURLMapping
from src.db.models.impl.annotation.url_type.user.sqlalchemy import AnnotationURLTypeUser
from src.db.models.impl.flag.url_validated.enums import URLType
from tests.automated.integration.api.annotate.anonymous.helper import get_next_url_for_anonymous_annotation, \
    post_and_get_next_url_for_anonymous_annotation
from tests.automated.integration.conftest import MOCK_USER_ID
from tests.helpers.data_creator.models.creation_info.us_state import USStateCreationInfo
from tests.helpers.setup.final_review.core import setup_for_get_next_url_for_final_review
from tests.helpers.setup.final_review.model import FinalReviewSetupInfo


@pytest.mark.asyncio
async def test_post_annotate_return_no_annotation(
    api_test_helper,
    pennsylvania: USStateCreationInfo,
    test_agency_id: int
):
    """
    If the `return_new_annotation` query arg is false,
    do not return a new annotation.
    """
    ath = api_test_helper
    ddc = ath.db_data_creator
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

    get_response_1: GetNextURLForAnonymousAnnotationResponse = await get_next_url_for_anonymous_annotation(rv)
    session_id = get_response_1.session_id

    post_response_1: GetNextURLForAnonymousAnnotationResponse = await post_and_get_next_url_for_anonymous_annotation(
        rv,
        url_mapping_1.url_id,
        AllAnnotationPostInfo(
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
        session_id=session_id,
        get_next_url=False
    )

    assert post_response_1.next_annotation is None

    url_types: list[AnnotationURLTypeUser] = await ddc.adb_client.get_all(AnnotationURLTypeUser)
    assert len(url_types) == 3
    annotation_url_type: AnnotationURLTypeUser = url_types[-1]
    assert annotation_url_type.user_id == MOCK_USER_ID
    assert annotation_url_type.url_id == get_response_1.next_annotation.url_info.url_id
    assert annotation_url_type.type == URLType.DATA_SOURCE
