from datetime import datetime

from pydantic import BaseModel


class SubmittedURLInfo(BaseModel):
    url_id: int
    data_source_id: int | None
    request_error: str | None
    submitted_at: datetime | None = None