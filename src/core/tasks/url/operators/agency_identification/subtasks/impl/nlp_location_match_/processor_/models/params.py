from pydantic import BaseModel


class NLPLocationMatchParams(BaseModel):
    url_id: int
    html: str 