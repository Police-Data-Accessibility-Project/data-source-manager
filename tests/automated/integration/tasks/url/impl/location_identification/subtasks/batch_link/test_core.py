import pytest

from src.core.tasks.url.operators.location_id.core import LocationIdentificationTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.annotation.location.auto.subtask.enums import LocationIDSubtaskType
from src.db.models.impl.annotation.location.auto.subtask.sqlalchemy import AnnotationLocationAutoSubtask
from src.db.models.impl.annotation.location.auto.suggestion.sqlalchemy import AnnotationLocationAutoSuggestion
from src.db.models.impl.link.location_batch.sqlalchemy import LinkLocationBatch
from tests.helpers.batch_creation_parameters.core import TestBatchCreationParameters
from tests.helpers.batch_creation_parameters.url_creation_parameters import TestURLCreationParameters
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.data_creator.models.creation_info.batch.v2 import BatchURLCreationInfoV2
from tests.helpers.data_creator.models.creation_info.locality import LocalityCreationInfo
from tests.helpers.run import run_task_and_confirm_success


@pytest.mark.asyncio
async def test_batch_link_subtask(
    operator: LocationIdentificationTaskOperator,
    db_data_creator: DBDataCreator,
    pittsburgh_locality: LocalityCreationInfo
):

    adb_client: AsyncDatabaseClient = operator.adb_client

    creation_info: BatchURLCreationInfoV2 = await db_data_creator.batch_v2(
        parameters=TestBatchCreationParameters(
            urls=[
                TestURLCreationParameters(
                    count=2
                )
            ]
        )
    )
    batch_id: int = creation_info.batch_id
    url_ids: list[int] = creation_info.url_ids

    location_id: int = pittsburgh_locality.location_id

    link = LinkLocationBatch(
        location_id=location_id,
        batch_id=batch_id
    )
    await adb_client.add(link)

    assert await operator.meets_task_prerequisites()
    assert operator._subtask == LocationIDSubtaskType.BATCH_LINK

    await run_task_and_confirm_success(operator)

    assert not await operator.meets_task_prerequisites()
    assert operator._subtask is None

    subtasks: list[AnnotationLocationAutoSubtask] = await adb_client.get_all(AnnotationLocationAutoSubtask)
    assert len(subtasks) == 2
    subtask: AnnotationLocationAutoSubtask = subtasks[0]
    assert subtask.type == LocationIDSubtaskType.BATCH_LINK
    assert subtask.locations_found

    suggestions: list[AnnotationLocationAutoSuggestion] = await adb_client.get_all(AnnotationLocationAutoSuggestion)
    assert len(suggestions) == 2

    assert all(sugg.confidence == 80 for sugg in suggestions)
    assert all(sugg.location_id == location_id for sugg in suggestions)