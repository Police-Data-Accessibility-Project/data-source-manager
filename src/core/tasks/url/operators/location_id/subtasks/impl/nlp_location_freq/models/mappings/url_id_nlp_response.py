from pydantic import BaseModel

from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.processor.nlp.models.response import \
    NLPLocationMatchResponse


class URLToNLPResponseMapping(BaseModel):
    url_id: int
    nlp_response: NLPLocationMatchResponse