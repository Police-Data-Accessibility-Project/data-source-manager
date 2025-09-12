from unittest.mock import AsyncMock, MagicMock

import pytest

from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.url.operators.agency_identification.core import AgencyIdentificationTaskOperator
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.models.input import \
    NLPLocationMatchSubtaskInput
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.core import \
    AgencyIDSubtaskInternalProcessor
from src.core.tasks.url.operators.agency_identification.subtasks.models.subtask import AutoAgencyIDSubtaskData
from src.core.tasks.url.operators.agency_identification.subtasks.models.suggestion import AgencySuggestion
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.link.task_url import LinkTaskURL
from src.db.models.impl.url.error_info.sqlalchemy import URLErrorInfo
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType
from src.db.models.impl.url.suggestion.agency.subtask.pydantic import URLAutoAgencyIDSubtaskPydantic
from src.db.models.impl.url.suggestion.agency.subtask.sqlalchemy import URLAutoAgencyIDSubtask
from src.db.models.impl.url.suggestion.agency.suggestion.sqlalchemy import AgencyIDSubtaskSuggestion
from tests.helpers.asserts import assert_task_run_success
from tests.helpers.data_creator.core import DBDataCreator

PATCH_ROOT = (
    "src.core.tasks.url.operators.agency_identification.subtasks." +
    "impl.nlp_location_match_.core.AgencyIDSubtaskInternalProcessor.process"
)



@pytest.mark.asyncio
async def test_nlp_location_match(
    operator: AgencyIdentificationTaskOperator,
    db_data_creator: DBDataCreator,
    url_ids: list[int],
    monkeypatch
):
    # Confirm operator meets prerequisites
    assert await operator.meets_task_prerequisites()
    assert operator._subtask == AutoAgencyIDSubtaskType.NLP_LOCATION_MATCH

    happy_path_url_id: int = url_ids[0]
    error_url_id: int = url_ids[1]

    agency_ids: list[int] = await db_data_creator.create_agencies(count=2)
    agency_id_25: int = agency_ids[0]
    agency_id_75: int = agency_ids[1]

    async def mock_process_response(
        self: AgencyIDSubtaskInternalProcessor,
        inputs: list[NLPLocationMatchSubtaskInput],
    ) -> list[AutoAgencyIDSubtaskData]:
        response = [
            AutoAgencyIDSubtaskData(
                pydantic_model=URLAutoAgencyIDSubtaskPydantic(
                    task_id=self._task_id,
                    url_id=happy_path_url_id,
                    type=AutoAgencyIDSubtaskType.NLP_LOCATION_MATCH,
                    agencies_found=True,
                ),
                suggestions=[
                    AgencySuggestion(
                        agency_id=agency_id_25,
                        confidence=25
                    ),
                    AgencySuggestion(
                        agency_id=agency_id_75,
                        confidence=75
                    )
                ]
            ),
            AutoAgencyIDSubtaskData(
                pydantic_model=URLAutoAgencyIDSubtaskPydantic(
                    task_id=self._task_id,
                    url_id=error_url_id,
                    type=AutoAgencyIDSubtaskType.NLP_LOCATION_MATCH,
                    agencies_found=False,
                ),
                suggestions=[],
                error="Test error"
            )
        ]
        return response

    monkeypatch.setattr(AgencyIDSubtaskInternalProcessor, "process", mock_process_response)
    run_info: TaskOperatorRunInfo = await operator.run_task()
    assert_task_run_success(run_info)

    adb_client: AsyncDatabaseClient = operator.adb_client
    # Confirm two URLs linked to the task
    task_links: list[LinkTaskURL] = await adb_client.get_all(LinkTaskURL)
    assert len(task_links) == 2
    assert {task_link.url_id for task_link in task_links} == set(url_ids)
    assert {task_link.task_id for task_link in task_links} == {operator._task_id}

    # Confirm two subtasks were created
    subtasks: list[URLAutoAgencyIDSubtask] = await adb_client.get_all(URLAutoAgencyIDSubtask)
    assert len(subtasks) == 2
    assert {subtask.url_id for subtask in subtasks} == set(url_ids)
    assert {subtask.task_id for subtask in subtasks} == {operator._task_id}
    assert {subtask.type for subtask in subtasks} == {AutoAgencyIDSubtaskType.NLP_LOCATION_MATCH}
    assert {subtask.agencies_found for subtask in subtasks} == {True, False}


    # Confirm one URL error info
    error_infos: list[URLErrorInfo] = await adb_client.get_all(URLErrorInfo)
    assert len(error_infos) == 1
    assert error_infos[0].task_id == operator._task_id
    assert error_infos[0].url_id == error_url_id
    assert error_infos[0].error == "Test error"

    # Confirm two suggestions for happy path URL id
    suggestions: list[AgencyIDSubtaskSuggestion] = await adb_client.get_all(AgencyIDSubtaskSuggestion)
    assert len(suggestions) == 2
    # Confirm expected agency ids
    assert {suggestion.agency_id for suggestion in suggestions} == set(agency_ids)
    # Confirm both have the expected confidence values
    assert {suggestion.confidence for suggestion in suggestions} == {25, 75}

