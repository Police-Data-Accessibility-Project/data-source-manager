from pydantic import BaseModel


class USStateCreationInfo(BaseModel):
    us_state_id: int
    location_id: int