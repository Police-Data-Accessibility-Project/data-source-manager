from pydantic import BaseModel

from src.core.enums import RecordType
from src.db.models.impl.flag.url_validated.enums import URLType


class URLSuggestionRequest(BaseModel):
    url: str
    url_type: URLType | None = None
    record_type: RecordType | None = None
    agency_ids: list[int] = []
    location_ids: list[int] = []
    name: str | None = None