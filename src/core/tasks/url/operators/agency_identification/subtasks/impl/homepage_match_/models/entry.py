from pydantic import BaseModel, Field

from src.db.models.impl.url.suggestion.agency.subtask.enum import SubtaskDetailCode


class GetHomepageMatchParams(BaseModel):
    url_id: int
    agency_id: int
    confidence: int = Field(..., ge=0, le=100)
    detail_code: SubtaskDetailCode