from pydantic import BaseModel


class AgencySuggestion(BaseModel):
    agency_id: int
    confidence: int