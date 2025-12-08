from pydantic import BaseModel, Field

from src.api.endpoints.annotate.all.get.models.suggestion import SuggestionModel
from src.core.enums import RecordType

class RecordTypeSuggestionModel(BaseModel):
    record_type: RecordType
    user_count: int
    robo_confidence: int | None = Field(
        description="The robo labeler's given confidence for its suggestion. Null if no robo-label occurred.",
        ge=0,
        le=100,
    )

class RecordTypeAnnotationResponseOuterInfo(BaseModel):
    suggestions: list[RecordTypeSuggestionModel]

