from pydantic import BaseModel

from src.collectors.enums import URLStatus
from src.db.models.impl.flag.url_validated.enums import URLType


class SubmitDataSourceURLDuplicateSubmissionResponse(BaseModel):
    message: str
    url_id: int
    url_type: URLType | None
    url_status: URLStatus