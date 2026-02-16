import pytest

from src.core.tasks.url.operators.agency_identification.core import AgencyIdentificationTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.annotation.agency.auto.subtask.enum import AutoAgencyIDSubtaskType
from src.db.models.impl.annotation.agency.auto.subtask.sqlalchemy import AnnotationAgencyAutoSubtask
from src.db.models.impl.annotation.agency.auto.suggestion.sqlalchemy import AnnotationAgencyAutoSuggestion
from src.db.models.impl.link.agency_batch.sqlalchemy import LinkAgencyBatch
from tests.helpers.batch_creation_parameters.core import TestBatchCreationParameters
from tests.helpers.batch_creation_parameters.url_creation_parameters import TestURLCreationParameters
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.data_creator.models.creation_info.batch.v2 import BatchURLCreationInfoV2
from tests.helpers.run import run_task_and_confirm_success


@pytest.mark.asyncio
async def test_batch_link_subtask(
    operator: AgencyIdentificationTaskOperator,
    db_data_creator: DBDataCreator
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

    agency_id: int = await db_data_creator.agency()

    link = LinkAgencyBatch(
        agency_id=agency_id,
        batch_id=batch_id
    )
    await adb_client.add(link)

    assert await operator.meets_task_prerequisites()
    assert operator._subtask == AutoAgencyIDSubtaskType.BATCH_LINK

    await run_task_and_confirm_success(operator)

    assert not await operator.meets_task_prerequisites()
    assert operator._subtask is None

    subtasks: list[AnnotationAgencyAutoSubtask] = await adb_client.get_all(AnnotationAgencyAutoSubtask)
    assert len(subtasks) == 2
    subtask: AnnotationAgencyAutoSubtask = subtasks[0]
    assert subtask.type == AutoAgencyIDSubtaskType.BATCH_LINK

    assert subtask.agencies_found

    suggestions: list[AnnotationAgencyAutoSuggestion] = await adb_client.get_all(AnnotationAgencyAutoSuggestion)
    assert len(suggestions) == 2

    assert all(sugg.confidence == 80 for sugg in suggestions)
    assert all(sugg.agency_id == agency_id for sugg in suggestions)


