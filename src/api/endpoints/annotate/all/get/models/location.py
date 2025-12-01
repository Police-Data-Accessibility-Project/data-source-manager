from pydantic import BaseModel, Field


class LocationAnnotationSuggestion(BaseModel):
    location_id: int
    location_name: str
    user_count: int
    robo_confidence: int | None = Field(
        description="The robo labeler's given confidence for its suggestion. Null if no robo-label occurred.",
        ge=0,
        le=100,
    )

class LocationAnnotationResponseOuterInfo(BaseModel):
    suggestions: list[LocationAnnotationSuggestion]
    not_found_count: int = Field(
        description="How many users indicated the location could not be found."
    )