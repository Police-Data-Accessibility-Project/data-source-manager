from pydantic import BaseModel


class CountyCreationInfo(BaseModel):
    county_id: int
    location_id: int