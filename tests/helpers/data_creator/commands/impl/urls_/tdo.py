from datetime import datetime

from pydantic import BaseModel

from src.core.enums import RecordType


class SubmittedURLInfo(BaseModel):
    url_id: int
    data_source_id: int | None
    request_error: str | None
    submitted_at: datetime | None = None