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

# TODO: Replace Usages and Delete
class LocationAnnotationAutoSuggestion(BaseModel):
    location_id: int
    location_name: str = Field(
        title="The full name of the location"
    )
    confidence: int = Field(
        title="The confidence of the location",
        ge=0,
        le=100,
    )

# TODO: Replace Usages and Delete
class LocationAnnotationUserSuggestion(BaseModel):
    location_id: int
    location_name: str = Field(
        title="The full name of the location"
    )
    user_count: int = Field(
        title="The number of users who suggested this location",
        ge=1,
    )

# TODO: Replace Usages and Delete
class LocationAnnotationUserSuggestionOuterInfo(BaseModel):
    suggestions: list[LocationAnnotationUserSuggestion]
    not_found_count: int = Field(
        title="How many users listed the location as not found.",
        ge=0,
    )

class LocationAnnotationResponseOuterInfo(BaseModel):
    suggestions: list[LocationAnnotationSuggestion]
    not_found_count: int = Field(
        description="How many users indicated the location could not be found."
    )