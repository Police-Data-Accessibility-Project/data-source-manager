from pydantic import BaseModel, Field


class AgencyAnnotationAutoSuggestion(BaseModel):
    agency_id: int
    agency_name: str
    confidence: int = Field(
        title="The confidence of the location",
        ge=0,
        le=100,
    )

class AgencyAnnotationUserSuggestion(BaseModel):
    agency_id: int
    agency_name: str
    user_count: int

class AgencyAnnotationUserSuggestionOuterInfo(BaseModel):
    suggestions: list[AgencyAnnotationUserSuggestion]
    not_found_count: int = Field(
        title="How many users listed the agency as not found.",
        ge=0,
    )

class AgencyAnnotationResponseOuterInfo(BaseModel):
    user: AgencyAnnotationUserSuggestionOuterInfo
    auto: list[AgencyAnnotationAutoSuggestion]