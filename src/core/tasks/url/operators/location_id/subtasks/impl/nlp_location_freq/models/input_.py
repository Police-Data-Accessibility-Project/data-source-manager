from pydantic import BaseModel


class NLPLocationFrequencySubtaskInput(BaseModel):
    url_id: int
    html: str