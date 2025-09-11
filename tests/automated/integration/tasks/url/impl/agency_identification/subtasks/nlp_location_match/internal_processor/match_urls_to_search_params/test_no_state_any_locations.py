import pytest

from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.core import \
    AgencyIDSubtaskInternalProcessor


@pytest.mark.asyncio()
async def test_no_state_any_locations(
    internal_processor: AgencyIDSubtaskInternalProcessor,
):
    """
    Test that when an input has no US State and any locations
    that the result is not returned
    """