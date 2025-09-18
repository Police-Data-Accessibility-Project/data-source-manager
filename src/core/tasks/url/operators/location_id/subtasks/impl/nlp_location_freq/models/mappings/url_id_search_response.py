from pydantic import BaseModel

from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.processor.query_.models.response import \
    SearchSimilarLocationsResponse
from src.external.pdap.dtos.search_agency_by_location.response import SearchAgencyByLocationResponse


class URLToSearchResponseMapping(BaseModel):
    url_id: int
    search_responses: list[SearchSimilarLocationsResponse]