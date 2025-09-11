import pytest

from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.core import \
    AgencyIDSubtaskInternalProcessor


@pytest.mark.asyncio()
async def test_state_no_locations(
    internal_processor: AgencyIDSubtaskInternalProcessor,
):
    """
    Test that when an input has a US State and no locations
    then no result is returned
    """