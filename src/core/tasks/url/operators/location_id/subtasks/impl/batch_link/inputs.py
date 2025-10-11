from pydantic import BaseModel


class LocationBatchLinkInput(BaseModel):
    location_id: int
    url_id: int