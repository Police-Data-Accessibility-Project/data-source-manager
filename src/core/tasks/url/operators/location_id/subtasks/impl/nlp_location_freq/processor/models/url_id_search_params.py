from pydantic import BaseModel

from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.processor.query_.models.params import \
    SearchSimilarLocationsParams
from src.external.pdap.dtos.search_agency_by_location.params import SearchAgencyByLocationParams


class URLToSearchParamsMapping(BaseModel):
    url_id: int
    search_params: list[SearchSimilarLocationsParams]

    @property
    def is_empty(self) -> bool:
        return len(self.search_params) == 0