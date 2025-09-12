import pytest

from tests.automated.integration.api.conftest import MOCK_USER_ID
from tests.helpers.setup.annotate_agency.core import setup_for_annotate_agency
from tests.helpers.setup.annotate_agency.model import AnnotateAgencySetupInfo


@pytest.mark.asyncio
async def test_annotate_agency_other_user_annotation(api_test_helper):
    """
    Test Scenario: Other User Annotation
    A URL has been annotated by another User
    Our user should still receive this URL to annotate
    """
    ath = api_test_helper
    setup_info: AnnotateAgencySetupInfo = await setup_for_annotate_agency(
        db_data_creator=ath.db_data_creator,
        url_count=1
    )
    url_ids = setup_info.url_ids

    response = await ath.request_validator.get_next_agency_annotation()

    assert response.next_annotation
    next_annotation = response.next_annotation
    # Check that url_id matches the one we inserted
    assert next_annotation.url_info.url_id == url_ids[0]

    # Check that html data is present
    assert next_annotation.html_info.description != ""
    assert next_annotation.html_info.title != ""

    # Check that one agency_suggestion exists
    assert len(next_annotation.agency_suggestions) == 1

    # Test that another user can insert a suggestion
    await ath.db_data_creator.manual_suggestion(
        user_id=MOCK_USER_ID + 1,
        url_id=url_ids[0],
    )

    # After this, text that our user does not receive this URL
    response = await ath.request_validator.get_next_agency_annotation()
    assert response.next_annotation is None
