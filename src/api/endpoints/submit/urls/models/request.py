from pydantic import BaseModel


class URLSubmissionRequest(BaseModel):
    urls: list[str]