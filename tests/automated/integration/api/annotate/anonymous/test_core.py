from uuid import UUID

import pytest

from src.api.endpoints.annotate.all.get.models.name import NameAnnotationSuggestion
from src.api.endpoints.annotate.all.get.models.response import GetNextURLForAllAnnotationResponse
from src.api.endpoints.annotate.all.post.models.agency import AnnotationPostAgencyInfo
from src.api.endpoints.annotate.all.post.models.location import AnnotationPostLocationInfo
from src.api.endpoints.annotate.all.post.models.name import AnnotationPostNameInfo
from src.api.endpoints.annotate.all.post.models.request import AllAnnotationPostInfo
from src.api.endpoints.annotate.anonymous.get.response import GetNextURLForAnonymousAnnotationResponse
from src.core.enums import RecordType
from src.db.dtos.url.mapping_.simple import SimpleURLMapping
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.url.suggestion.anonymous.agency.sqlalchemy import AnonymousAnnotationAgency
from src.db.models.impl.url.suggestion.anonymous.location.sqlalchemy import AnonymousAnnotationLocation
from src.db.models.impl.url.suggestion.anonymous.record_type.sqlalchemy import AnonymousAnnotationRecordType
from src.db.models.impl.url.suggestion.anonymous.url_type.sqlalchemy import AnonymousAnnotationURLType
from src.db.models.mixins import URLDependentMixin
from tests.automated.integration.api.annotate.anonymous.helper import get_next_url_for_anonymous_annotation, \
    post_and_get_next_url_for_anonymous_annotation
from tests.helpers.data_creator.models.creation_info.us_state import USStateCreationInfo
from tests.helpers.setup.final_review.core import setup_for_get_next_url_for_final_review
from tests.helpers.setup.final_review.model import FinalReviewSetupInfo


@pytest.mark.asyncio
async def test_annotate_anonymous(
    api_test_helper,
    pennsylvania: USStateCreationInfo,
):

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
    session_id: UUID = get_response_1.session_id
    assert session_id is not None
    assert get_response_1.next_annotation is not None
    assert len(get_response_1.next_annotation.name_suggestions) == 1
    name_suggestion: NameAnnotationSuggestion = get_response_1.next_annotation.name_suggestions[0]
    assert name_suggestion.name is not None
    assert name_suggestion.endorsement_count == 0

    agency_id: int = await ddc.agency()

    post_response_1: GetNextURLForAnonymousAnnotationResponse = await post_and_get_next_url_for_anonymous_annotation(
        rv,
        get_response_1.next_annotation.url_info.url_id,
        AllAnnotationPostInfo(
            suggested_status=URLType.DATA_SOURCE,
            record_type=RecordType.ACCIDENT_REPORTS,
            agency_info=AnnotationPostAgencyInfo(agency_ids=[agency_id]),
            location_info=AnnotationPostLocationInfo(
                location_ids=[
                    pennsylvania.location_id,
                ]
            ),
            name_info=AnnotationPostNameInfo(
                new_name="New Name"
            )
        ),
        session_id=session_id
    )
    assert post_response_1.session_id == session_id


    assert post_response_1.next_annotation is not None
    assert post_response_1.next_annotation.url_info.url_id != get_response_1.next_annotation.url_info.url_id

    for model in [
        AnonymousAnnotationAgency,
        AnonymousAnnotationLocation,
        AnonymousAnnotationRecordType,
        AnonymousAnnotationURLType
    ]:
        instances: list[URLDependentMixin] = await ddc.adb_client.get_all(model)
        assert len(instances) == 1
        instance: model = instances[0]
        assert instance.url_id == get_response_1.next_annotation.url_info.url_id

    # Run again without giving session ID, confirm original URL returned
    get_response_2: GetNextURLForAnonymousAnnotationResponse = await get_next_url_for_anonymous_annotation(rv)
    assert get_response_2.session_id != session_id
    assert get_response_2.next_annotation is not None
    assert get_response_2.next_annotation.url_info.url_id == get_response_1.next_annotation.url_info.url_id

    # Run again while giving session ID, confirm second URL returned
    get_response_3: GetNextURLForAnonymousAnnotationResponse = await get_next_url_for_anonymous_annotation(rv, session_id)
    assert get_response_3.session_id == session_id
    assert get_response_3.next_annotation is not None
    assert get_response_3.next_annotation.url_info.url_id == post_response_1.next_annotation.url_info.url_id

