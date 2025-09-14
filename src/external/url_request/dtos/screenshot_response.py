from pydantic import BaseModel


class URLScreenshotResponse(BaseModel):
    url: str
    screenshot: bytes | None
    error: str | None = None

    @property
    def is_success(self) -> bool:
        return self.error is None