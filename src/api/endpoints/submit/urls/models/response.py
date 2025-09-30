from pydantic import BaseModel

from src.api.endpoints.submit.urls.enums import URLBatchSubmissionStatus, URLSubmissionStatus


class URLSubmissionResponse(BaseModel):
    url_original: str
    url_cleaned: str | None = None
    status: URLSubmissionStatus
    url_id: int | None = None

class URLBatchSubmissionResponse(BaseModel):
    status: URLBatchSubmissionStatus
    batch_id: int | None
    urls: list[URLSubmissionResponse]