from pydantic import BaseModel


class AgencyPostResponse(BaseModel):
    agency_id: int