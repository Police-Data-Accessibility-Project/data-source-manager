import pytest

from src.core.tasks.url.operators.location_id.core import LocationIdentificationTaskOperator
from src.db.models.impl.url.suggestion.location.auto.subtask.enums import LocationIDSubtaskType
from tests.helpers.data_creator.core import DBDataCreator


@pytest.mark.asyncio
async def test_survey_flag(
    operator: LocationIdentificationTaskOperator,
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

    await db_data_creator.add_compressed_html([applicable_url_id])

    # Confirm prerequisite met and subtask if Agency Location Frequency
    assert await operator.meets_task_prerequisites()
    assert operator._subtask == LocationIDSubtaskType.NLP_LOCATION_FREQUENCY

    # Set flag to disable NLP Location Frequency Subtask
    monkeypatch.setenv(
        "LOCATION_ID_NLP_LOCATION_MATCH_FLAG", "0"
    )

    # Confirm prerequisite no longer met.
    assert not await operator.meets_task_prerequisites()
