from pydantic import BaseModel, Field

class AgencyAnnotationSuggestion(BaseModel):
    agency_id: int
    agency_name: str
    user_count: int
    robo_confidence: int | None = Field(
        description="The robo labeler's given confidence for its suggestion. Null if no robo-label occurred.",
        ge=0,
        le=100,
    )

# TODO: Replace Usages and Delete
class AgencyAnnotationAutoSuggestion(BaseModel):
    agency_id: int
    agency_name: str
    confidence: int = Field(
        title="The confidence of the location",
        ge=0,
        le=100,
    )

# TODO: Replace Usages and Delete
class AgencyAnnotationUserSuggestion(BaseModel):
    agency_id: int
    agency_name: str
    user_count: int

# TODO: Replace Usages and Delete
class AgencyAnnotationUserSuggestionOuterInfo(BaseModel):
    suggestions: list[AgencyAnnotationUserSuggestion]
    not_found_count: int = Field(
        title="How many users listed the agency as not found.",
        ge=0,
    )

class AgencyAnnotationResponseOuterInfo(BaseModel):
    suggestions: list[AgencyAnnotationSuggestion]
    not_found_count: int = Field(
        description="How many users indicated the agency could not be found."
    )
