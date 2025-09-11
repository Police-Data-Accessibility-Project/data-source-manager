from pydantic import BaseModel

from src.external.pdap.dtos.search_agency_by_location.params import SearchAgencyByLocationParams


class URLToSearchParamsMapping(BaseModel):
    url_id: int
    search_params: list[SearchAgencyByLocationParams]