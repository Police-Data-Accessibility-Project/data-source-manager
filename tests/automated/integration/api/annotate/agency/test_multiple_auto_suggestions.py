import pytest

from src.core.enums import SuggestionType
from tests.helpers.data_creator.models.creation_info.batch.v1 import BatchURLCreationInfo


@pytest.mark.asyncio
async def test_annotate_agency_multiple_auto_suggestions(api_test_helper):
    """
    Test Scenario: Multiple Auto Suggestions
    A URL has multiple Agency Auto Suggestion and has not been annotated by the User
    The user should receive all of the auto suggestions with full detail
    """
    ath = api_test_helper
    buci: BatchURLCreationInfo = await ath.db_data_creator.batch_and_urls(
        url_count=1,
        with_html_content=True
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

    # Check that html data is present
    assert next_annotation.html_info.description != ""
    assert next_annotation.html_info.title != ""

    # Check that two agency_suggestions exist
    assert len(next_annotation.agency_suggestions) == 2

    for agency_suggestion in next_annotation.agency_suggestions:
        assert agency_suggestion.suggestion_type == SuggestionType.AUTO_SUGGESTION
        assert agency_suggestion.pdap_agency_id is not None
        assert agency_suggestion.agency_name is not None
        assert agency_suggestion.state is not None
        assert agency_suggestion.county is not None
        assert agency_suggestion.locality is not None
