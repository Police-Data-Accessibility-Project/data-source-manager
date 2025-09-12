from pydantic import BaseModel

from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.nlp.models.us_state import \
    USState


class NLPLocationMatchResponse(BaseModel):
    locations: list[str]
    us_state: USState | None

    @property
    def valid(self) -> bool:
        # Valid responses must have a US State and at least one location
        if self.us_state is None:
            return False
        if len(self.locations) == 0:
            return False
        return True
