from pydantic import BaseModel, Field, model_validator

from src.util.models.full_url import FullURL


class URLProbeResponse(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    url: FullURL
    status_code: int | None = Field(le=999, ge=100)
    content_type: str | None
    error: str | None = None

    @model_validator(mode='after')
    def check_error_mutually_exclusive_with_content(self):
        if self.error is None:
            if self.status_code is None:
                raise ValueError('Status code required if no error')
            return self

        if self.content_type is not None:
            raise ValueError('Content type mutually exclusive with error')

        return self

