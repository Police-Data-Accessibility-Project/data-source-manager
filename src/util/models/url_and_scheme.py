from pydantic import BaseModel


class URLAndScheme(BaseModel):
    url: str
    scheme: str | None