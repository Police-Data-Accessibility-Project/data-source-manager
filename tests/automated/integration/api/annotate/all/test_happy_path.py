import pytest

from src.api.endpoints.annotate.all.get.models.response import GetNextURLForAllAnnotationResponse
from src.api.endpoints.annotate.all.get.models.suggestion import SuggestionModel
from src.api.endpoints.annotate.all.get.queries.core import GetNextURLForAllAnnotationQueryBuilder
from src.api.endpoints.annotate.all.post.models.agency import AnnotationPostAgencyInfo
from src.api.endpoints.annotate.all.post.models.location import AnnotationPostLocationInfo
from src.api.endpoints.annotate.all.post.models.name import AnnotationPostNameInfo
from src.api.endpoints.annotate.all.post.models.request import AllAnnotationPostInfo
from src.core.enums import RecordType
from src.db.models.impl.annotation.agency.user.sqlalchemy import AnnotationAgencyUser
from src.db.models.impl.annotation.location.user.sqlalchemy import AnnotationLocationUser
from src.db.models.impl.annotation.name.suggestion.sqlalchemy import AnnotationNameSuggestion
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.annotation.name.user.sqlalchemy import LinkUserNameSuggestion
from src.db.models.impl.annotation.record_type.user.user import AnnotationUserRecordType
from src.db.models.impl.annotation.url_type.user.sqlalchemy import AnnotationUserURLType
from tests.helpers.data_creator.models.creation_info.us_state import USStateCreationInfo
from tests.helpers.setup.final_review.core import setup_for_get_next_url_for_final_review


@pytest.mark.asyncio
async def test_annotate_all(
    api_test_helper,
    pennsylvania: USStateCreationInfo,
    allegheny_county: USStateCreationInfo,
    california: USStateCreationInfo,
    test_agency_id: int
):
    """
    Test the happy path workflow for the all-annotations endpoint
    The user should be able to get a valid URL (filtering on batch id if needed),
    submit a full annotation, and receive another URL
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

    # Get a valid URL to annotate
    get_response_1 = await ath.request_validator.get_next_url_for_all_annotations()
    assert get_response_1.next_annotation is not None
    assert len(get_response_1.next_annotation.name_suggestions.suggestions) == 1
    name_suggestion = get_response_1.next_annotation.name_suggestions.suggestions[0]
    assert name_suggestion.display_name is not None
    assert name_suggestion.user_count == 0

    # Apply the second batch id as a filter and see that a different URL is returned
    get_response_2 = await ath.request_validator.get_next_url_for_all_annotations(
        batch_id=setup_info_2.batch_id
    )

    assert get_response_2.next_annotation is not None
    assert get_response_1.next_annotation.url_info.url_id != get_response_2.next_annotation.url_info.url_id

    # Annotate the first and submit
    agency_id = await ath.db_data_creator.agency()
    post_response_1 = await ath.request_validator.post_all_annotations_and_get_next(
        url_id=url_mapping_1.url_id,
        all_annotations_post_info=AllAnnotationPostInfo(
            suggested_status=URLType.DATA_SOURCE,
            record_type=RecordType.ACCIDENT_REPORTS,
            agency_info=AnnotationPostAgencyInfo(agency_ids=[agency_id]),
            location_info=AnnotationPostLocationInfo(
                location_ids=[
                    california.location_id,
                    pennsylvania.location_id,
                ]
            ),
            name_info=AnnotationPostNameInfo(
                new_name="New Name"
            )
        )
    )
    assert post_response_1.next_annotation is not None

    # Confirm the second is received
    assert post_response_1.next_annotation.url_info.url_id == url_mapping_2.url_id

    # Upon submitting the second, confirm that no more URLs are returned through either POST or GET
    post_response_2 = await ath.request_validator.post_all_annotations_and_get_next(
        url_id=url_mapping_2.url_id,
        all_annotations_post_info=AllAnnotationPostInfo(
            suggested_status=URLType.NOT_RELEVANT,
            location_info=AnnotationPostLocationInfo(),
            agency_info=AnnotationPostAgencyInfo(),
            name_info=AnnotationPostNameInfo(
                existing_name_id=setup_info_2.name_suggestion_id
            )
        )
    )
    assert post_response_2.next_annotation is None

    get_response_3 = await ath.request_validator.get_next_url_for_all_annotations()
    assert get_response_3.next_annotation is None


    # Check that all annotations are present in the database

    # Check URL Type Suggestions
    all_relevance_suggestions: list[AnnotationUserURLType] = await adb_client.get_all(AnnotationUserURLType)
    assert len(all_relevance_suggestions) == 4
    suggested_types: set[URLType] = {sugg.type for sugg in all_relevance_suggestions}
    assert suggested_types == {URLType.DATA_SOURCE, URLType.NOT_RELEVANT}

    # Should be one agency
    all_agency_suggestions = await adb_client.get_all(AnnotationAgencyUser)
    assert len(all_agency_suggestions) == 3
    suggested_agency_ids: set[int] = {sugg.agency_id for sugg in all_agency_suggestions}
    assert agency_id in suggested_agency_ids

    # Should be one record type
    all_record_type_suggestions = await adb_client.get_all(AnnotationUserRecordType)
    assert len(all_record_type_suggestions) == 3
    suggested_record_types: set[RecordType] = {
        sugg.record_type for sugg in all_record_type_suggestions
    }
    assert RecordType.ACCIDENT_REPORTS.value in suggested_record_types

    # Confirm 3 Location Suggestions, with two belonging to California and one to Pennsylvania
    all_location_suggestions = await adb_client.get_all(AnnotationLocationUser)
    assert len(all_location_suggestions) == 2
    location_ids: list[int] = [location_suggestion.location_id for location_suggestion in all_location_suggestions]
    assert set(location_ids) == {california.location_id, pennsylvania.location_id}
    # Confirm that all location suggestions are for the correct URL
    for location_suggestion in all_location_suggestions:
        assert location_suggestion.url_id == url_mapping_1.url_id

    # Retrieve the same URL (directly from the database, leveraging a different User)
    # And confirm the presence of the user annotations
    response: GetNextURLForAllAnnotationResponse = await adb_client.run_query_builder(
        GetNextURLForAllAnnotationQueryBuilder(
            batch_id=None,
            user_id=99,
        )
    )
    suggestions: list[SuggestionModel] = response.next_annotation.location_suggestions.suggestions
    assert len(suggestions) == 2

    response_location_ids: list[int] = [
        location_suggestion.id
        for location_suggestion in suggestions]

    assert set(response_location_ids) == {
        california.location_id,
        pennsylvania.location_id
    }

    response_location_names: list[str] = [
        location_suggestion.display_name
        for location_suggestion in suggestions]
    assert set(response_location_names) == {
        "California",
        "Pennsylvania"
    }

    for user_suggestion in suggestions:
        assert user_suggestion.user_count == 1

    # Confirm 3 name suggestions
    name_suggestions: list[AnnotationNameSuggestion] = await adb_client.get_all(AnnotationNameSuggestion)
    assert len(name_suggestions) == 3
    suggested_names: set[str] = {name_suggestion.suggestion for name_suggestion in name_suggestions}
    assert "New Name" in suggested_names

    # Confirm 2 link user name suggestions
    link_user_name_suggestions: list[LinkUserNameSuggestion] = await adb_client.get_all(LinkUserNameSuggestion)
    assert len(link_user_name_suggestions) == 2

