from pydantic import BaseModel

from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.models.mappings.url_id_nlp_response import \
    URLToNLPResponseMapping


class NLPResponseSubsets(BaseModel):
    valid: list[URLToNLPResponseMapping]
    invalid: list[URLToNLPResponseMapping]