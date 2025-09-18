import pytest

from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.processor.nlp.models import \
    NLPLocationMatchResponse
from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.processor.nlp.models.us_state import \
    USState

US_STATE = USState(
    name="Pennsylvania",
    iso="PA",
)

SINGLE_LOCATION: list[str] = ["Pittsburgh"]
MULTIPLE_LOCATION: list[str] = ["Pittsburgh", "Allegheny"]

@pytest.mark.parametrize(
    argnames="nlp_response, expected_result",
    argvalues=[
        (
            NLPLocationMatchResponse(
                locations=SINGLE_LOCATION,
                us_state=US_STATE
            ),
            True,
        ),
        (
            NLPLocationMatchResponse(
                locations=MULTIPLE_LOCATION,
                us_state=US_STATE,
            ),
            True
        ),
        (
            NLPLocationMatchResponse(
                locations=MULTIPLE_LOCATION,
                us_state=None,
            ),
            False,
        ),
        (
            NLPLocationMatchResponse(
                locations=[],
                us_state=US_STATE,
            ),
            False,
        ),
        (
            NLPLocationMatchResponse(
                locations=[],
                us_state=None,
            ),
            False
        )
    ],
)
def test_nlp_response_valid(nlp_response: NLPLocationMatchResponse, expected_result: bool):
    assert nlp_response.valid == expected_result