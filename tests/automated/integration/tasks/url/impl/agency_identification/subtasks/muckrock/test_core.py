from unittest.mock import MagicMock

import pytest

from src.collectors.enums import CollectorType
from src.collectors.impl.muckrock.api_interface.core import MuckrockAPIInterface
from src.collectors.impl.muckrock.api_interface.lookup_response import AgencyLookupResponse
from src.collectors.impl.muckrock.enums import AgencyLookupResponseType
from src.core.enums import SuggestionType
from src.core.tasks.base.run_info import TaskOperatorRunInfo
from src.core.tasks.url.operators.agency_identification.core import AgencyIdentificationTaskOperator
from src.core.tasks.url.operators.agency_identification.dtos.suggestion import URLAgencySuggestionInfo
from src.core.tasks.url.operators.agency_identification.subtasks.impl.muckrock_.core import MuckrockAgencyIDSubtaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType
from src.db.models.impl.url.suggestion.agency.subtask.sqlalchemy import URLAutoAgencyIDSubtask
from src.db.models.impl.url.suggestion.agency.suggestion.sqlalchemy import AgencyIDSubtaskSuggestion
from src.external.pdap.client import PDAPClient
from src.external.pdap.dtos.match_agency.post import MatchAgencyInfo
from src.external.pdap.dtos.match_agency.response import MatchAgencyResponse
from src.external.pdap.enums import MatchAgencyResponseStatus
from tests.helpers.asserts import assert_task_run_success
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_muckrock_subtask(
    operator: AgencyIdentificationTaskOperator,
    db_data_creator: DBDataCreator
):
    adb_client: AsyncDatabaseClient = operator.adb_client

    # Run basic survey and confirm no next subtask
    assert not await operator.meets_task_prerequisites()
    assert operator._subtask is None

    # Add validated URL and confirm no next subtask
    await db_data_creator.create_validated_urls(count=1)

    assert not await operator.meets_task_prerequisites()
    assert operator._subtask is None

    # Add unvalidated URL without collector type
    inapplicable_url_id: int = (await db_data_creator.create_urls(count=1))[0].url_id

    # Should still not have subtask
    assert not await operator.meets_task_prerequisites()
    assert operator._subtask is None

    # Create Auto Googler batch and link to validated URL
    inapplicable_batch_id: int = await db_data_creator.create_batch(
        strategy=CollectorType.AUTO_GOOGLER
    )
    await db_data_creator.create_batch_url_links(
        url_ids=[inapplicable_url_id],
        batch_id=inapplicable_batch_id
    )

    # Confirm prerequisite not met
    assert not await operator.meets_task_prerequisites()
    assert operator._subtask is None

    # Create Muckrock batch and link to validated URL
    applicable_url_id: int = (
        await db_data_creator.create_urls(
            count=1,
            collector_metadata={
                "agency": 123
            }
        )
    )[0].url_id
    applicable_batch_id: int = await db_data_creator.create_batch(
        strategy=CollectorType.MUCKROCK_SIMPLE_SEARCH
    )
    await db_data_creator.create_batch_url_links(
        url_ids=[applicable_url_id],
        batch_id=applicable_batch_id
    )

    # Confirm prerequisite met and subtask is Muckrock
    assert await operator.meets_task_prerequisites()
    assert operator._subtask == AutoAgencyIDSubtaskType.MUCKROCK

    # Test that muckrock subtask correctly sends agency name to
    # MatchAgenciesInterface and adds received suggestions to
    # url_agency_suggestions

    # Create mock instances for dependency injections
    muckrock_api_interface_mock = operator.loader._muckrock_api_interface
    pdap_client_mock = operator.loader._pdap_client

    # Set up mock return values for method calls
    muckrock_api_interface_mock.lookup_agency.return_value = AgencyLookupResponse(
        type=AgencyLookupResponseType.FOUND,
        name="Mock Agency Name",
        error=None
    )

    # Create agencies
    await db_data_creator.create_agency(1)
    await db_data_creator.create_agency(2)

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
    assert subtask.type == AutoAgencyIDSubtaskType.MUCKROCK
    assert subtask.url_id == applicable_url_id
    subtask_id: int = subtask.id

    suggestions: list[AgencyIDSubtaskSuggestion] = await adb_client.get_all(
        AgencyIDSubtaskSuggestion
    )
    assert len(suggestions) == 2
    assert {suggestion.confidence for suggestion in suggestions} == {50}
    assert {suggestion.agency_id for suggestion in suggestions} == {1, 2}
    assert {suggestion.subtask_id for suggestion in suggestions} == {subtask_id}


    # # Assert methods called as expected
    muckrock_api_interface_mock.lookup_agency.assert_called_once_with(
        muckrock_agency_id=123
    )
    pdap_client_mock.match_agency.assert_called_once_with(
        name="Mock Agency Name"
    )
