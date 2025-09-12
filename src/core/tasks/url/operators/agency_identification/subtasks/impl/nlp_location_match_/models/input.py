from pydantic import BaseModel


class NLPLocationMatchSubtaskInput(BaseModel):
    url_id: int
    html: str