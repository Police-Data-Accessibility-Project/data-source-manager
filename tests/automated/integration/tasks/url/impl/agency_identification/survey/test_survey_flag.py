import pytest

from src.collectors.enums import CollectorType
from src.core.tasks.url.operators.agency_identification.core import AgencyIdentificationTaskOperator
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType
from tests.helpers.data_creator.core import DBDataCreator

@pytest.mark.asyncio
async def test_survey_flag(
    operator: AgencyIdentificationTaskOperator,
    db_data_creator: DBDataCreator,
    monkeypatch
):
    """
    Test that survey correctly disables Subtask flags
    when the environment variable is set to disable that subtask
    """

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

    # Set flag to disable CKAN Subtask
    monkeypatch.setenv(
        "AGENCY_ID_CKAN_FLAG", "0"
    )

    # Confirm prerequisite no longer met.
    assert not await operator.meets_task_prerequisites()