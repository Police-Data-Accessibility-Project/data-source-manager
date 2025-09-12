from pydantic import BaseModel

from src.external.pdap.dtos.search_agency_by_location.response import SearchAgencyByLocationResponse


class URLToSearchResponseMapping(BaseModel):
    url_id: int
    search_responses: list[SearchAgencyByLocationResponse]