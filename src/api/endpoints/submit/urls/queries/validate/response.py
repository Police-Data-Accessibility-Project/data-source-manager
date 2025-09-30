from pydantic import BaseModel


class ValidateURLResponse(BaseModel):
    valid_urls: list[str]
    invalid_urls: list[str]