from pydantic import BaseModel

from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.materialized_views.url_status.enums import URLStatusEnum


class SubmitDataSourceURLDuplicateSubmissionResponse(BaseModel):
    message: str
    url_id: int
    url_type: URLType | None
    url_status: URLStatusEnum