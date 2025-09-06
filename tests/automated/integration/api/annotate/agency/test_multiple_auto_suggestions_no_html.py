import pytest

from src.core.enums import SuggestionType
from tests.helpers.data_creator.models.creation_info.batch.v1 import BatchURLCreationInfo


@pytest.mark.asyncio
async def test_annotate_agency_multiple_auto_suggestions_no_html(api_test_helper):
    """
    Test Scenario: Multiple Auto Suggestions
    A URL has multiple Agency Auto Suggestion and has not been annotated by the User
    The user should receive all of the auto suggestions with full detail
    """
    ath = api_test_helper
    buci: BatchURLCreationInfo = await ath.db_data_creator.batch_and_urls(
        url_count=1,
        with_html_content=False
    )
    await ath.db_data_creator.auto_suggestions(
        url_ids=buci.url_ids,
        num_suggestions=2,
        suggestion_type=SuggestionType.AUTO_SUGGESTION
    )

    # User requests next annotation
    response = await ath.request_validator.get_next_agency_annotation()

    assert response.next_annotation
    next_annotation = response.next_annotation
    # Check that url_id matches the one we inserted
    assert next_annotation.url_info.url_id == buci.url_ids[0]

    # Check that html data is not present
    assert next_annotation.html_info.description == ""
    assert next_annotation.html_info.title == ""
