from pydantic import BaseModel


class LocalityCreationInfo(BaseModel):
    locality_id: int
    location_id: int