import pytest

from src.core.tasks.url.operators.auto_name.core import AutoNameURLTaskOperator
from src.db.models.impl.annotation.name.suggestion.enums import NameSuggestionSource
from src.db.models.impl.annotation.name.suggestion.sqlalchemy import AnnotationNameSuggestion
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.run import run_task_and_confirm_success


@pytest.mark.asyncio
async def test_core(
    operator: AutoNameURLTaskOperator,
    db_data_creator: DBDataCreator
):

    assert not await operator.meets_task_prerequisites()

    # Create URL
    url_id: int = (await db_data_creator.create_urls(count=1))[0].url_id

    assert not await operator.meets_task_prerequisites()

    # Add HTML content

    await db_data_creator.html_data(url_ids=[url_id])

    assert await operator.meets_task_prerequisites()

    await run_task_and_confirm_success(operator)

    assert not await operator.meets_task_prerequisites()

    # Confirm suggestion was added
    suggestions: list[AnnotationNameSuggestion] = await db_data_creator.adb_client.get_all(AnnotationNameSuggestion)
    assert len(suggestions) == 1
    suggestion: AnnotationNameSuggestion = suggestions[0]
    assert suggestion.url_id == url_id
    assert suggestion.suggestion == "test html content"
    assert suggestion.source == NameSuggestionSource.HTML_METADATA_TITLE