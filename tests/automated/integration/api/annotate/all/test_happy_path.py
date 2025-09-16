import pytest

from src.api.endpoints.annotate.agency.post.dto import URLAgencyAnnotationPostInfo
from src.api.endpoints.annotate.all.post.models.request import AllAnnotationPostInfo
from src.core.enums import SuggestedStatus, RecordType
from src.db.models.impl.url.suggestion.agency.user import UserUrlAgencySuggestion
from src.db.models.impl.url.suggestion.record_type.user import UserRecordTypeSuggestion
from src.db.models.impl.url.suggestion.relevant.user import UserRelevantSuggestion
from tests.helpers.setup.final_review.core import setup_for_get_next_url_for_final_review


@pytest.mark.asyncio
async def test_annotate_all(api_test_helper):
    """
    Test the happy path workflow for the all-annotations endpoint
    The user should be able to get a valid URL (filtering on batch id if needed),
    submit a full annotation, and receive another URL
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
    url_mapping_2 = setup_info_2.url_mapping

    # First, get a valid URL to annotate
    get_response_1 = await ath.request_validator.get_next_url_for_all_annotations()
    assert get_response_1.next_annotation is not None

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
            suggested_status=SuggestedStatus.RELEVANT,
            record_type=RecordType.ACCIDENT_REPORTS,
            agency=URLAgencyAnnotationPostInfo(
                is_new=False,
                suggested_agency=agency_id
            ),
            location_ids=[]
        )
    )
    assert post_response_1.next_annotation is not None

    # Confirm the second is received
    assert post_response_1.next_annotation.url_info.url_id == url_mapping_2.url_id

    # Upon submitting the second, confirm that no more URLs are returned through either POST or GET
    post_response_2 = await ath.request_validator.post_all_annotations_and_get_next(
        url_id=url_mapping_2.url_id,
        all_annotations_post_info=AllAnnotationPostInfo(
            suggested_status=SuggestedStatus.NOT_RELEVANT,
            location_ids=[]
        )
    )
    assert post_response_2.next_annotation is None

    get_response_3 = await ath.request_validator.get_next_url_for_all_annotations()
    assert get_response_3.next_annotation is None


    # Check that all annotations are present in the database

    # Should be two relevance annotations, one True and one False
    all_relevance_suggestions: list[UserRelevantSuggestion] = await adb_client.get_all(UserRelevantSuggestion)
    assert len(all_relevance_suggestions) == 2
    assert all_relevance_suggestions[0].suggested_status == SuggestedStatus.RELEVANT.value
    assert all_relevance_suggestions[1].suggested_status == SuggestedStatus.NOT_RELEVANT.value

    # Should be one agency
    all_agency_suggestions = await adb_client.get_all(UserUrlAgencySuggestion)
    assert len(all_agency_suggestions) == 1
    assert all_agency_suggestions[0].is_new == False
    assert all_agency_suggestions[0].agency_id == agency_id

    # Should be one record type
    all_record_type_suggestions = await adb_client.get_all(UserRecordTypeSuggestion)
    assert len(all_record_type_suggestions) == 1
    assert all_record_type_suggestions[0].record_type == RecordType.ACCIDENT_REPORTS.value
