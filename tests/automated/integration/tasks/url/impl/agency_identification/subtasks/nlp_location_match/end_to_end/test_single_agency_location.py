import pytest

from src.core.tasks.url.operators.agency_identification.core import AgencyIdentificationTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType
from src.db.models.impl.url.suggestion.agency.subtask.sqlalchemy import URLAutoAgencyIDSubtask
from src.db.models.impl.url.suggestion.agency.suggestion.sqlalchemy import AgencyIDSubtaskSuggestion
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.data_creator.models.creation_info.county import CountyCreationInfo
from tests.helpers.data_creator.models.creation_info.locality import LocalityCreationInfo
from tests.helpers.run import run_task_and_confirm_success


@pytest.mark.asyncio
async def test_single_agency_location(
    operator: AgencyIdentificationTaskOperator,
    db_data_creator: DBDataCreator,
    pittsburgh_locality: LocalityCreationInfo,
    allegheny_county: CountyCreationInfo,
    url_id: int
):
    adb_client: AsyncDatabaseClient = operator.adb_client

    # Confirm operator does not meet prerequisites yet
    assert not await operator.meets_task_prerequisites()

    # Add a location suggestion that has one agency linked to it

    # Add location suggestion for two locations
    await db_data_creator.add_location_suggestion(
        url_id=url_id,
        location_ids=[
            allegheny_county.location_id,
            pittsburgh_locality.location_id
        ],
        confidence=68,
    )
    # Confirm operator does not yet meet prerequisites
    assert not await operator.meets_task_prerequisites()

    # Create agency
    agency_id: int = await db_data_creator.agency()
    # Link agency to pittsburgh
    await db_data_creator.link_agencies_to_location(
        agency_ids=[agency_id],
        location_id=pittsburgh_locality.location_id
    )

    # Confirm operator now meets prerequisites
    assert await operator.meets_task_prerequisites()

    # Confirm next task is nlp location match
    assert operator._subtask == AutoAgencyIDSubtaskType.NLP_LOCATION_MATCH

    # Run operator and confirm runs without error
    await run_task_and_confirm_success(operator)

    # Confirm subtask no longer meets prerequisites
    assert not await operator.meets_task_prerequisites()

    # Check for presence of subtask
    subtasks: list[URLAutoAgencyIDSubtask] = await adb_client.get_all(URLAutoAgencyIDSubtask)
    assert len(subtasks) == 1
    subtask: URLAutoAgencyIDSubtask = subtasks[0]
    assert subtask.type == AutoAgencyIDSubtaskType.NLP_LOCATION_MATCH

    # Confirm subtask lists agencies found
    assert subtask.agencies_found

    # Confirm single agency suggestion in database
    suggestions: list[AgencyIDSubtaskSuggestion] = await adb_client.get_all(AgencyIDSubtaskSuggestion)
    assert len(suggestions) == 1

    # Confirm confidence of agency suggestion equal to location suggestion
    suggestion: AgencyIDSubtaskSuggestion = suggestions[0]
    assert suggestion.confidence == 68
