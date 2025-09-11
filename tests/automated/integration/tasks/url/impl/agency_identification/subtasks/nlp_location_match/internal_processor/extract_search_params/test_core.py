import pytest

from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.models.input import \
    NLPLocationMatchSubtaskInput
from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.core import \
    AgencyIDSubtaskInternalProcessor



@pytest.mark.asyncio
async def test_core(
    internal_processor: AgencyIDSubtaskInternalProcessor
):
    # Define NLPLocationMatchSubtaskInputs
    inputs: list[NLPLocationMatchSubtaskInput] = [
        NLPLocationMatchSubtaskInput(
            url_id=1,
            html="<html>State and multiple locations</html>"
        ),
        NLPLocationMatchSubtaskInput(
            url_id=2,
            html="<html>Single location</html>"
        ),
        NLPLocationMatchSubtaskInput(
            url_id=3,
            html="<html>No location</html>"
        )
    ]


    # Set _get_location_match responses


    # Run _extract_search_params


    # Validate results

    # Validate counter

    # Validate mapper