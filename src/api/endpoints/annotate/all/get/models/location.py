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


class LocationAnnotationResponseOuterInfo(BaseModel):
    user: list[LocationAnnotationUserSuggestion]
    auto: list[LocationAnnotationAutoSuggestion]