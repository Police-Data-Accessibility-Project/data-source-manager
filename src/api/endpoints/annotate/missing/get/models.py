from pydantic import BaseModel, Field


class MissingAnnotationQueueEntry(BaseModel):
    url_id: int = Field(
        description="The URL ID in the missing location/agency queue."
    )
    url: str = Field(
        description="The URL string."
    )
    missing_location_count: int = Field(
        description="Number of users who marked the location as missing."
    )
    missing_agency_count: int = Field(
        description="Number of users who marked the agency as missing."
    )


class MissingAnnotationQueueResponse(BaseModel):
    entries: list[MissingAnnotationQueueEntry]
