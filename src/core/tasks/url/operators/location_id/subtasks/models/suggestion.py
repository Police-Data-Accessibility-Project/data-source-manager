from pydantic import BaseModel, Field


class LocationSuggestion(BaseModel):
    location_id: int
    confidence: int = Field(ge=0, le=100)