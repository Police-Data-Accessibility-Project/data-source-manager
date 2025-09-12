import pytest

from src.api.endpoints.annotate.agency.post.dto import URLAgencyAnnotationPostInfo
from src.db.models.impl.url.suggestion.agency.user import UserUrlAgencySuggestion
from tests.helpers.setup.annotate_agency.core import setup_for_annotate_agency
from tests.helpers.setup.annotate_agency.model import AnnotateAgencySetupInfo


@pytest.mark.asyncio
async def test_annotate_agency_submit_new(api_test_helper):
    """
    Test Scenario: Submit New
    Our user receives an annotation and marks it as `NEW`
    This should complete successfully
    And within the database the annotation should be marked as `NEW`
    """
    ath = api_test_helper
    adb_client = ath.adb_client()
    setup_info: AnnotateAgencySetupInfo = await setup_for_annotate_agency(
        db_data_creator=ath.db_data_creator,
        url_count=1
    )
    url_ids = setup_info.url_ids

    # User should submit an annotation and mark it as New
    response = await ath.request_validator.post_agency_annotation_and_get_next(
        url_id=url_ids[0],
        agency_annotation_post_info=URLAgencyAnnotationPostInfo(
            suggested_agency=await ath.db_data_creator.agency(),
            is_new=True
        )
    )
    assert response.next_annotation is None

    # Within database, the annotation should be marked as `NEW`
    all_manual_suggestions = await adb_client.get_all(UserUrlAgencySuggestion)
    assert len(all_manual_suggestions) == 1
    assert all_manual_suggestions[0].is_new
