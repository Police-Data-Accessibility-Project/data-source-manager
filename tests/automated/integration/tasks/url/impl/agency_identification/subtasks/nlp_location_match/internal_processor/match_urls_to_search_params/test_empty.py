import pytest

from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.core import \
    AgencyIDSubtaskInternalProcessor


@pytest.mark.asyncio()
async def test_empty(
    internal_processor: AgencyIDSubtaskInternalProcessor,
):
    """
    Test that when an input has no US State or locations,
    that result is not returned
    """