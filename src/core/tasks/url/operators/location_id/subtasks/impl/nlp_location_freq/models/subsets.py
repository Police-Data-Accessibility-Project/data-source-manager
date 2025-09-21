from pydantic import BaseModel

from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.models.mappings.url_id_nlp_response import \
    URLToNLPResponseMapping


class NLPResponseSubsets(BaseModel):
    valid: list[URLToNLPResponseMapping]
    invalid: list[URLToNLPResponseMapping]