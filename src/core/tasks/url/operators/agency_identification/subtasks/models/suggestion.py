from pydantic import BaseModel, Field


class AgencySuggestion(BaseModel):
    agency_id: int
    confidence: int = Field(ge=0, le=100)