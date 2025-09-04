import pytest

from src.collectors.enums import URLStatus
from src.core.enums import BatchStatus
from src.db.client.async_ import AsyncDatabaseClient
from src.db.enums import TaskType
from src.db.models.exceptions import WriteToViewError
from src.db.models.impl.task.core import Task
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType, SubtaskDetailCode
from src.db.models.impl.url.suggestion.agency.subtask.sqlalchemy import URLAutoAgencyIDSubtask
from src.db.models.views.has_agency_auto_suggestion import HasAgencyAutoSuggestionView

@pytest.mark.asyncio
async def test_has_agency_auto_suggestion_view(
    adb_client_test: AsyncDatabaseClient
) -> None:
    """Test functionality of agency auto suggestion view and view logic in general."""

    view_objects: list[HasAgencyAutoSuggestionView] = \
        await adb_client_test.get_all(HasAgencyAutoSuggestionView)

    assert len(view_objects) == 0

    url = URL(
        url="https://example.com/1",
        status=URLStatus.OK,
        source=URLSource.COLLECTOR
    )
    url_id: int = await adb_client_test.add(url, return_id=True)

    view_objects: list[HasAgencyAutoSuggestionView] = \
        await adb_client_test.get_all(HasAgencyAutoSuggestionView)

    assert len(view_objects) == 1
    assert view_objects[0].url_id == url_id
    assert view_objects[0].has_agency_suggestions is False


    task = Task(
        task_type=TaskType.HTML.value,
        task_status=BatchStatus.READY_TO_LABEL,
    )
    task_id: int = await adb_client_test.add(task, return_id=True)

    subtask = URLAutoAgencyIDSubtask(
        task_id=task_id,
        url_id=url_id,
        subtask=AutoAgencyIDSubtaskType.CKAN,
        agencies_found=False,
        detail=SubtaskDetailCode.RETRIEVAL_ERROR
    )
    await adb_client_test.add(subtask)

    view_objects: list[HasAgencyAutoSuggestionView] = \
        await adb_client_test.get_all(HasAgencyAutoSuggestionView)

    assert len(view_objects) == 1
    assert view_objects[0].url_id == url_id
    assert view_objects[0].has_agency_suggestions is True


    view_obj_to_add = HasAgencyAutoSuggestionView(
        url_id=1,
        has_agency_suggestions=True
    )

    with pytest.raises(WriteToViewError):
        await adb_client_test.add(view_obj_to_add)