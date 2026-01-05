from uuid import UUID

import pytest

from src.api.endpoints.annotate.all.get.models.name import NameAnnotationSuggestion
from src.api.endpoints.annotate.all.post.models.agency import AnnotationPostAgencyInfo
from src.api.endpoints.annotate.all.post.models.location import AnnotationPostLocationInfo
from src.api.endpoints.annotate.all.post.models.name import AnnotationPostNameInfo
from src.api.endpoints.annotate.all.post.models.request import AllAnnotationPostInfo
from src.api.endpoints.annotate.anonymous.get.response import GetNextURLForAnonymousAnnotationResponse
from src.api.shared.models.message_response import MessageResponse
from src.core.enums import RecordType
from src.db.dtos.url.mapping_.simple import SimpleURLMapping
from src.db.models.impl.annotation.agency.anon.sqlalchemy import AnnotationAgencyAnon
from src.db.models.impl.annotation.agency.user.sqlalchemy import AnnotationAgencyUser
from src.db.models.impl.annotation.location.anon.sqlalchemy import AnnotationLocationAnon
from src.db.models.impl.annotation.location.user.sqlalchemy import AnnotationLocationUser
from src.db.models.impl.annotation.name.anon.sqlalchemy import AnnotationNameAnonEndorsement
from src.db.models.impl.annotation.name.suggestion.sqlalchemy import AnnotationNameSuggestion
from src.db.models.impl.annotation.name.user.sqlalchemy import AnnotationNameUserEndorsement
from src.db.models.impl.annotation.record_type.anon.sqlalchemy import AnnotationRecordTypeAnon
from src.db.models.impl.annotation.record_type.user.user import AnnotationRecordTypeUser
from src.db.models.impl.annotation.url_type.anon.sqlalchemy import AnnotationURLTypeAnon
from src.db.models.impl.annotation.url_type.user.sqlalchemy import AnnotationURLTypeUser
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.mixins import URLDependentMixin
from tests.automated.integration.api.annotate.anonymous.helper import get_next_url_for_anonymous_annotation, \
    post_and_get_next_url_for_anonymous_annotation
from tests.automated.integration.conftest import MOCK_USER_ID
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
    assert len(get_response_1.next_annotation.name_suggestions.suggestions) == 1
    name_suggestion: NameAnnotationSuggestion = get_response_1.next_annotation.name_suggestions.suggestions[0]
    assert name_suggestion.display_name is not None
    assert name_suggestion.user_count == 0

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
        AnnotationAgencyAnon,
        AnnotationLocationAnon,
        AnnotationRecordTypeAnon,
        AnnotationURLTypeAnon
    ]:
        instances: list[URLDependentMixin] = await ddc.adb_client.get_all(model)
        assert len(instances) == 1
        instance: model = instances[0]
        assert instance.url_id == get_response_1.next_annotation.url_info.url_id

    # Check for existence of name suggestion (2 were added by setup)
    name_suggestions: list[AnnotationNameSuggestion] = await ddc.adb_client.get_all(AnnotationNameSuggestion)
    assert len(name_suggestions) == 3

    # Check for existence of link
    link_instances: list[AnnotationNameAnonEndorsement] = await ddc.adb_client.get_all(AnnotationNameAnonEndorsement)
    assert len(link_instances) == 1
    link_instance: AnnotationNameAnonEndorsement = link_instances[0]
    assert link_instance.session_id == session_id

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

    ### TEST MIGRATION ###
    # Call the migration endpoint with a user ID, and confirm all anonymous annotations have transferred to the user.
    response: MessageResponse = rv.post_v3(
        f'/annotate/migrate?session_id={session_id}',
        expected_model=MessageResponse,
    )
    assert response.message == 'Annotations migrated successfully.'

    # Check all annotations

    # URL Types
    url_types: list[AnnotationURLTypeUser] = await ddc.adb_client.get_all(AnnotationURLTypeUser)
    assert len(url_types) == 3
    annotation_url_type: AnnotationURLTypeUser = url_types[-1]
    assert annotation_url_type.user_id == MOCK_USER_ID
    assert annotation_url_type.url_id == get_response_1.next_annotation.url_info.url_id
    assert annotation_url_type.type == URLType.DATA_SOURCE

    # Locations
    locations: list[AnnotationLocationUser] = await ddc.adb_client.get_all(AnnotationLocationUser)
    assert len(locations) == 1
    annotation_location: AnnotationLocationUser = locations[0]
    assert annotation_location.user_id == MOCK_USER_ID
    assert annotation_location.url_id == get_response_1.next_annotation.url_info.url_id
    assert annotation_location.location_id == pennsylvania.location_id

    # Agencies
    agencies: list[AnnotationAgencyUser] = await ddc.adb_client.get_all(AnnotationAgencyUser)
    assert len(agencies) == 3
    annotation_agency: AnnotationAgencyUser = agencies[-1]
    assert annotation_agency.user_id == MOCK_USER_ID
    assert annotation_agency.url_id == get_response_1.next_annotation.url_info.url_id
    assert annotation_agency.agency_id == agency_id

    # Record Types
    record_types: list[AnnotationRecordTypeUser] = await ddc.adb_client.get_all(AnnotationRecordTypeUser)
    assert len(record_types) == 3
    annotation_record_type: AnnotationRecordTypeUser = record_types[-1]
    assert annotation_record_type.user_id == MOCK_USER_ID
    assert annotation_record_type.url_id == get_response_1.next_annotation.url_info.url_id
    assert annotation_record_type.record_type == RecordType.ACCIDENT_REPORTS.value

    # Name Suggestions
    name_suggestions: list[AnnotationNameUserEndorsement] = await ddc.adb_client.get_all(AnnotationNameUserEndorsement)
    assert len(name_suggestions) == 1
    annotation_name: AnnotationNameUserEndorsement = name_suggestions[0]
    assert annotation_name.user_id == MOCK_USER_ID