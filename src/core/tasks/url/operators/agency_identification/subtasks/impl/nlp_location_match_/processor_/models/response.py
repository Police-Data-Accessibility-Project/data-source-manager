from pydantic import BaseModel

from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor_.models.us_state import \
    USState


class NLPLocationMatchResponse(BaseModel):
    locations: list[str]
    us_state: USState | None