from pydantic import BaseModel, model_validator

from src.api.endpoints.submit.url.enums import URLSubmissionStatus


class URLSubmissionResponse(BaseModel):
    url_original: str
    url_cleaned: str | None = None
    status: URLSubmissionStatus
    url_id: int | None = None

    @model_validator(mode="after")
    def validate_url_id_if_accepted(self):
        if self.status in [URLSubmissionStatus.ACCEPTED_AS_IS, URLSubmissionStatus.ACCEPTED_WITH_CLEANING]:
            if self.url_id is None:
                raise ValueError("url_id is required for accepted urls")
        return self

