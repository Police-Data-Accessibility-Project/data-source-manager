from pydantic import BaseModel


class CheckUniqueURLResponse(BaseModel):
    unique_url: bool
    url_id: int | None