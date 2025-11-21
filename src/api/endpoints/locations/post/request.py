from pydantic import BaseModel


class AddLocationRequestModel(BaseModel):
    locality_name: str
    county_id: int
