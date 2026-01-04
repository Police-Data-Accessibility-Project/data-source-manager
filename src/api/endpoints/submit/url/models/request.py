from pydantic import BaseModel

from src.api.shared.models.request_base import RequestBase
from src.core.enums import RecordType


class URLSubmissionRequest(RequestBase):
    url: str
    record_type: RecordType | None = None
    name: str | None = None
    location_id: int | None = None
    agency_id: int | None = None
    description: str | None = None