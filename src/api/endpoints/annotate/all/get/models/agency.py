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

class AgencyAnnotationResponseOuterInfo(BaseModel):
    suggestions: list[AgencyAnnotationSuggestion]
    not_found_count: int = Field(
        description="How many users indicated the agency could not be found."
    )
