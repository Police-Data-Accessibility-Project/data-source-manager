import pytest
import uuid

from src.api.endpoints.annotate.all.get.models.response import GetNextURLForAllAnnotationResponse
from src.core.enums import RecordType
from src.db.models.impl.annotation.agency.anon.sqlalchemy import AnnotationAgencyAnon
from src.db.models.impl.annotation.location.anon.sqlalchemy import AnnotationLocationAnon
from src.db.models.impl.annotation.name.anon.sqlalchemy import AnnotationNameAnonEndorsement
from src.db.models.impl.annotation.name.suggestion.enums import NameSuggestionSource
from src.db.models.impl.annotation.name.suggestion.sqlalchemy import AnnotationNameSuggestion
from src.db.models.impl.annotation.record_type.anon.sqlalchemy import AnnotationRecordTypeAnon
from src.db.models.impl.annotation.url_type.anon.sqlalchemy import AnnotationURLTypeAnon
from src.db.models.impl.anon_session.sqlalchemy import AnonymousSession
from src.db.models.impl.flag.url_validated.enums import URLType
from tests.helpers.data_creator.models.creation_info.us_state import USStateCreationInfo
from tests.helpers.setup.final_review.core import setup_for_get_next_url_for_final_review


@pytest.mark.asyncio
async def test_anon_count(
    api_test_helper,
    test_agency_id: int,
    pennsylvania: USStateCreationInfo,
):
    """
    Test that the user annotation counts are updated correctly
    when anonymous annotations are added.
    """
    ath = api_test_helper
    adb_client = ath.adb_client()

    # Set up URLs
    setup_info_1 =  await setup_for_get_next_url_for_final_review(
        db_data_creator=ath.db_data_creator, include_user_annotations=True
    )
    url_id: int = setup_info_1.url_mapping.url_id

    # Add anonymous sessions
    anon_sessions: list[AnonymousSession] = []
    for i in range(12):
        anon_session = AnonymousSession(
            id=uuid.uuid4(),
        )
        anon_sessions.append(anon_session)
    await adb_client.add_all(anon_sessions)

    def get_anon_session_id(i: int) -> uuid.UUID:
        return anon_sessions[i].id


    # URL Types
    url_type_annotations: list[AnnotationURLTypeAnon] = []
    for i in range(3):
        url_type_annotation = AnnotationURLTypeAnon(
            url_id=url_id,
            session_id=get_anon_session_id(i),
            url_type=URLType.DATA_SOURCE
        )
        url_type_annotations.append(url_type_annotation)
    await adb_client.add_all(url_type_annotations)



    # Record Types
    record_type_annotations: list[AnnotationRecordTypeAnon] = []
    for i in range(5):
        record_type_annotation = AnnotationRecordTypeAnon(
            url_id=url_id,
            session_id=get_anon_session_id(i),
            record_type=RecordType.CAR_GPS
        )
        record_type_annotations.append(record_type_annotation)
    await adb_client.add_all(record_type_annotations)



    # Agencies
    agency_annotations: list[AnnotationAgencyAnon] = []
    for i in range(7):
        agency_annotation = AnnotationAgencyAnon(
            url_id=url_id,
            agency_id=test_agency_id,
            session_id=get_anon_session_id(i)
        )
        agency_annotations.append(agency_annotation)
    await adb_client.add_all(agency_annotations)


    # Locations
    location_annotations: list[AnnotationLocationAnon] = []
    for i in range(9):
        location_annotation = AnnotationLocationAnon(
            url_id=url_id,
            session_id=get_anon_session_id(i),
            location_id=pennsylvania.location_id,
        )
        location_annotations.append(location_annotation)
    await adb_client.add_all(location_annotations)

    # Name
    name_suggestion = AnnotationNameSuggestion(
        url_id=url_id,
        suggestion="Test Name",
        source=NameSuggestionSource.USER,
    )
    name_suggestion_id = await adb_client.add(name_suggestion, return_id=True)

    name_annotations: list[AnnotationNameAnonEndorsement] = []
    for i in range(11):
        name_annotation = AnnotationNameAnonEndorsement(
            suggestion_id=name_suggestion_id,
            session_id=get_anon_session_id(i),
        )
        name_annotations.append(name_annotation)
    await adb_client.add_all(name_annotations)

    # Check that the counts are correct
    get_response_1: GetNextURLForAllAnnotationResponse = await ath.request_validator.get_next_url_for_all_annotations()
    assert get_response_1.next_annotation is not None
    assert get_response_1.next_annotation.name_suggestions.suggestions[1].user_count == 5
    assert get_response_1.next_annotation.location_suggestions.suggestions[0].user_count == 4
    assert get_response_1.next_annotation.agency_suggestions.suggestions[0].user_count == 3
    assert get_response_1.next_annotation.record_type_suggestions.suggestions[0].user_count == 2
    assert get_response_1.next_annotation.url_type_suggestions[0].endorsement_count == 1
