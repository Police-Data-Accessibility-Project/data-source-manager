from pydantic import BaseModel


class URLScreenshotOutcome(BaseModel):
    url_id: int
    screenshot: bytes | None
    error: str | None

    @property
    def success(self) -> bool:
        return self.error is None