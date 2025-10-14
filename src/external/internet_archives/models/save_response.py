from pydantic import BaseModel


class InternetArchivesSaveResponseInfo(BaseModel):
    url: str
    error: str | None = None

    @property
    def has_error(self) -> bool:
        return self.error is not None