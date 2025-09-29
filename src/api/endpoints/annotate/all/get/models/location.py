from pydantic import BaseModel, Field


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


class LocationAnnotationUserSuggestion(BaseModel):
    location_id: int
    location_name: str = Field(
        title="The full name of the location"
    )
    user_count: int = Field(
        title="The number of users who suggested this location",
        ge=1,
    )

class LocationAnnotationUserSuggestionOuterInfo(BaseModel):
    suggestions: list[LocationAnnotationUserSuggestion]
    not_found_count: int = Field(
        title="How many users listed the location as not found.",
        ge=0,
    )

class LocationAnnotationResponseOuterInfo(BaseModel):
    user: LocationAnnotationUserSuggestionOuterInfo
    auto: list[LocationAnnotationAutoSuggestion]