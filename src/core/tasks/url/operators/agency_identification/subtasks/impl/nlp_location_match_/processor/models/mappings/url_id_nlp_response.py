from pydantic import BaseModel

from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.nlp.models.response import \
    NLPLocationMatchResponse


class URLToNLPResponseMapping(BaseModel):
    url_id: int
    nlp_response: NLPLocationMatchResponse