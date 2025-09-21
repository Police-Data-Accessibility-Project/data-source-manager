import pytest

from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.url.operators.location_id.core import LocationIdentificationTaskOperator
from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.core import \
    NLPLocationFrequencySubtaskOperator
from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.models.input_ import \
    NLPLocationFrequencySubtaskInput
from src.core.tasks.url.operators.location_id.subtasks.models.subtask import AutoLocationIDSubtaskData
from src.core.tasks.url.operators.location_id.subtasks.models.suggestion import LocationSuggestion
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.link.task_url import LinkTaskURL
from src.db.models.impl.url.error_info.sqlalchemy import URLErrorInfo
from src.db.models.impl.url.suggestion.location.auto.subtask.enums import LocationIDSubtaskType
from src.db.models.impl.url.suggestion.location.auto.subtask.pydantic import AutoLocationIDSubtaskPydantic
from src.db.models.impl.url.suggestion.location.auto.subtask.sqlalchemy import AutoLocationIDSubtask
from src.db.models.impl.url.suggestion.location.auto.suggestion.sqlalchemy import LocationIDSubtaskSuggestion
from tests.helpers.asserts import assert_task_run_success
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.data_creator.models.creation_info.county import CountyCreationInfo
from tests.helpers.data_creator.models.creation_info.locality import LocalityCreationInfo


@pytest.mark.asyncio
async def test_nlp_location_match(
    operator: LocationIdentificationTaskOperator,
    db_data_creator: DBDataCreator,
    url_ids: list[int],
    pittsburgh_locality: LocalityCreationInfo,
    allegheny_county: CountyCreationInfo,
    monkeypatch
):
    # Confirm operator meets prerequisites
    assert await operator.meets_task_prerequisites()
    assert operator._subtask == LocationIDSubtaskType.NLP_LOCATION_FREQUENCY

    happy_path_url_id: int = url_ids[0]
    error_url_id: int = url_ids[1]

    async def mock_process_inputs(
        self: NLPLocationFrequencySubtaskOperator,
        inputs: list[NLPLocationFrequencySubtaskInput],
    ) -> list[AutoLocationIDSubtaskData]:
        response = [
            AutoLocationIDSubtaskData(
                pydantic_model=AutoLocationIDSubtaskPydantic(
                    task_id=self.task_id,
                    url_id=happy_path_url_id,
                    type=LocationIDSubtaskType.NLP_LOCATION_FREQUENCY,
                    locations_found=True,
                ),
                suggestions=[
                    LocationSuggestion(
                        location_id=pittsburgh_locality.location_id,
                        confidence=25
                    ),
                    LocationSuggestion(
                        location_id=allegheny_county.location_id,
                        confidence=75
                    )
                ]
            ),
            AutoLocationIDSubtaskData(
                pydantic_model=AutoLocationIDSubtaskPydantic(
                    task_id=self.task_id,
                    url_id=error_url_id,
                    type=LocationIDSubtaskType.NLP_LOCATION_FREQUENCY,
                    locations_found=False,
                ),
                suggestions=[],
                error="Test error"
            )
        ]
        return response

    # Remove internal processor reference - mock NLP processor instead
    monkeypatch.setattr(
        NLPLocationFrequencySubtaskOperator,
        "_process_inputs",
        mock_process_inputs
    )
    run_info: TaskOperatorRunInfo = await operator.run_task()
    assert_task_run_success(run_info)

    adb_client: AsyncDatabaseClient = operator.adb_client
    # Confirm two URLs linked to the task
    task_links: list[LinkTaskURL] = await adb_client.get_all(LinkTaskURL)
    assert len(task_links) == 2
    assert {task_link.url_id for task_link in task_links} == set(url_ids)
    assert {task_link.task_id for task_link in task_links} == {operator._task_id}

    # Confirm two subtasks were created
    subtasks: list[AutoLocationIDSubtask] = await adb_client.get_all(AutoLocationIDSubtask)
    assert len(subtasks) == 2
    assert {subtask.url_id for subtask in subtasks} == set(url_ids)
    assert {subtask.task_id for subtask in subtasks} == {operator._task_id}
    assert {subtask.type for subtask in subtasks} == {
        LocationIDSubtaskType.NLP_LOCATION_FREQUENCY
    }
    assert {subtask.locations_found for subtask in subtasks} == {True, False}


    # Confirm one URL error info
    error_infos: list[URLErrorInfo] = await adb_client.get_all(URLErrorInfo)
    assert len(error_infos) == 1
    assert error_infos[0].task_id == operator._task_id
    assert error_infos[0].url_id == error_url_id
    assert error_infos[0].error == "Test error"

    # Confirm two suggestions for happy path URL id
    suggestions: list[LocationIDSubtaskSuggestion] = await adb_client.get_all(LocationIDSubtaskSuggestion)
    assert len(suggestions) == 2
    # Confirm expected agency ids
    assert {suggestion.location_id for suggestion in suggestions} == {
        pittsburgh_locality.location_id,
        allegheny_county.location_id,
    }
    # Confirm both have the expected confidence values
    assert {suggestion.confidence for suggestion in suggestions} == {25, 75}

