from pydantic import BaseModel


class AddLocationResponseModel(BaseModel):
    location_id: int