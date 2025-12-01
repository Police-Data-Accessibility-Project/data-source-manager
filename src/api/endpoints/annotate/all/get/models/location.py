from pydantic import BaseModel, Field

from src.api.endpoints.annotate.all.get.models.suggestion import SuggestionModel

class LocationAnnotationResponseOuterInfo(BaseModel):
    suggestions: list[SuggestionModel]
    not_found_count: int = Field(
        description="How many users indicated the location could not be found."
    )