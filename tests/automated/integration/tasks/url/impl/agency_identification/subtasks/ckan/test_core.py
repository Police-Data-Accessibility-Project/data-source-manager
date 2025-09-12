from unittest.mock import AsyncMock

import pytest

from src.collectors.enums import CollectorType
from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.url.operators.agency_identification.core import AgencyIdentificationTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType
from src.db.models.impl.url.suggestion.agency.subtask.sqlalchemy import URLAutoAgencyIDSubtask
from src.db.models.impl.url.suggestion.agency.suggestion.sqlalchemy import AgencyIDSubtaskSuggestion
from src.external.pdap.enums import MatchAgencyResponseStatus
from src.core.tasks.url.operators.agency_identification.subtasks.impl.ckan_.core import CKANAgencyIDSubtaskOperator
from src.core.enums import SuggestionType
from src.external.pdap.dtos.match_agency.response import MatchAgencyResponse
from src.external.pdap.dtos.match_agency.post import MatchAgencyInfo
from tests.helpers.asserts import assert_task_run_success
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_ckan_subtask(
    operator: AgencyIdentificationTaskOperator,
    db_data_creator: DBDataCreator
):
    # Test that ckan subtask correctly sends agency id to
    # CKANAPIInterface, sends resultant agency name to
    # PDAPClient and adds received suggestions to
    # url_agency_suggestions
    adb_client: AsyncDatabaseClient = operator.adb_client

    # Run basic survey and confirm no next subtask
    assert not await operator.meets_task_prerequisites()
    assert operator._subtask is None

    applicable_url_id: int = (
        await db_data_creator.create_urls(
            count=1,
            collector_metadata={
                "agency_name": "Test Agency"
            }
        )
    )[0].url_id
    applicable_batch_id: int = await db_data_creator.create_batch(
        strategy=CollectorType.CKAN
    )
    await db_data_creator.create_batch_url_links(
        url_ids=[applicable_url_id],
        batch_id=applicable_batch_id
    )

    # Confirm prerequisite met and subtask is CKAN
    assert await operator.meets_task_prerequisites()
    assert operator._subtask == AutoAgencyIDSubtaskType.CKAN

    pdap_client_mock = operator.loader._pdap_client
    pdap_client_mock.match_agency.return_value = MatchAgencyResponse(
        status=MatchAgencyResponseStatus.PARTIAL_MATCH,
        matches=[
            MatchAgencyInfo(
                id=1,
                submitted_name="Mock Agency Name",
            ),
            MatchAgencyInfo(
                id=2,
                submitted_name="Another Mock Agency Name",
            )
        ]
    )

    # Create agencies
    await db_data_creator.create_agency(1)
    await db_data_creator.create_agency(2)

    # Run the operator
    run_info: TaskOperatorRunInfo = await operator.run_task()
    assert_task_run_success(run_info)

    # Confirm prerequisite no longer met
    assert not await operator.meets_task_prerequisites()
    assert operator._subtask is None

    # Verify results
    subtasks: list[URLAutoAgencyIDSubtask] = await adb_client.get_all(URLAutoAgencyIDSubtask)
    assert len(subtasks) == 1
    subtask: URLAutoAgencyIDSubtask = subtasks[0]
    assert subtask.type == AutoAgencyIDSubtaskType.CKAN
    assert subtask.url_id == applicable_url_id
    subtask_id: int = subtask.id

    suggestions: list[AgencyIDSubtaskSuggestion] = await adb_client.get_all(
        AgencyIDSubtaskSuggestion
    )
    assert len(suggestions) == 2
    assert {suggestion.confidence for suggestion in suggestions} == {50}
    assert {suggestion.agency_id for suggestion in suggestions} == {1, 2}
    assert {suggestion.subtask_id for suggestion in suggestions} == {subtask_id}

    # Assert methods called as expected
    pdap_client_mock.match_agency.assert_called_once_with(name="Test Agency")
