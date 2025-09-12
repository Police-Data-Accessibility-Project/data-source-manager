import pytest

from tests.helpers.data_creator.models.creation_info.batch.v1 import BatchURLCreationInfo


@pytest.mark.asyncio
async def test_annotate_agency_single_confirmed_agency(api_test_helper):
    """
    Test Scenario: Single Confirmed Agency
    A URL has a single Confirmed Agency and has not been annotated by the User
    The user should not receive this URL to annotate
    """
    ath = api_test_helper
    buci: BatchURLCreationInfo = await ath.db_data_creator.batch_and_urls(
        url_count=1,
        with_html_content=True
    )
    await ath.db_data_creator.confirmed_suggestions(
        url_ids=buci.url_ids,
    )
    response = await ath.request_validator.get_next_agency_annotation()
    assert response.next_annotation is None
