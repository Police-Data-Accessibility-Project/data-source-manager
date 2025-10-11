from pydantic import BaseModel


class AgencyBatchLinkSubtaskParams(BaseModel):
    url_id: int
    agency_id: int