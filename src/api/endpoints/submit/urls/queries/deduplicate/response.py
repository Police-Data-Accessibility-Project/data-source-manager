from pydantic import BaseModel


class DeduplicateURLResponse(BaseModel):
    new_urls: list[str]
    duplicate_urls: list[str]