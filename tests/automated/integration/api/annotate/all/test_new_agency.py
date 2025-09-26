import pytest

from src.api.endpoints.annotate.all.post.models.agency import AnnotationPostAgencyInfo, \
    AnnotationNewAgencySuggestionInfo
from src.api.endpoints.annotate.all.post.models.name import AnnotationPostNameInfo
from src.api.endpoints.annotate.all.post.models.request import AllAnnotationPostInfo
from src.core.enums import RecordType
from src.db.models.impl.agency.enums import JurisdictionType, AgencyType
from src.db.models.impl.agency.suggestion.sqlalchemy import NewAgencySuggestion
from src.db.models.impl.flag.url_validated.enums import URLType
from tests.helpers.data_creator.models.creation_info.us_state import USStateCreationInfo
from tests.helpers.setup.final_review.core import setup_for_get_next_url_for_final_review
from tests.helpers.setup.final_review.model import FinalReviewSetupInfo


@pytest.mark.asyncio
async def test_add_new_agency(
    api_test_helper,
    pennsylvania: USStateCreationInfo,
):
    """
    Test the process for adding a new agency
    Confirm a new agency suggestion is successfully added in the database.
    """
    ath = api_test_helper
    adb_client = ath.adb_client()

    setup_info_1: FinalReviewSetupInfo =  await setup_for_get_next_url_for_final_review(
        db_data_creator=ath.db_data_creator,
        include_user_annotations=True
    )
    url_mapping_1 = setup_info_1.url_mapping

    post_response_1 = await ath.request_validator.post_all_annotations_and_get_next(
        url_id=url_mapping_1.url_id,
        all_annotations_post_info=AllAnnotationPostInfo(
            suggested_status=URLType.DATA_SOURCE,
            record_type=RecordType.ACCIDENT_REPORTS,
            agency_info=AnnotationPostAgencyInfo(
                new_agency_suggestion=AnnotationNewAgencySuggestionInfo(
                    name="New Agency",
                    location_id=pennsylvania.location_id,
                    jurisdiction_type=JurisdictionType.STATE,
                    agency_type=AgencyType.LAW_ENFORCEMENT,
                )
            ),
            location_ids=[
                pennsylvania.location_id,
            ],
            name_info=AnnotationPostNameInfo(
                new_name="New Name"
            )
        )
    )

    # Check for existence of new agency suggestion

    suggestions: list[NewAgencySuggestion] = await adb_client.get_all(NewAgencySuggestion)
    assert len(suggestions) == 1
    suggestion: NewAgencySuggestion = suggestions[0]
    assert suggestion.name == "New Agency"
    assert suggestion.location_id == pennsylvania.location_id
    assert suggestion.jurisdiction_type == JurisdictionType.STATE
    assert suggestion.agency_type == AgencyType.LAW_ENFORCEMENT