from pydantic import BaseModel

from src.core.enums import RecordType


class URLSubmissionRequest(BaseModel):
    url: str
    record_type: RecordType | None = None
    name: str | None = None
    location_id: int | None = None
    agency_id: int | None = None