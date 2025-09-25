from pydantic import BaseModel


class AutoNamePrerequisitesInput(BaseModel):
    url_id: int
    title: str