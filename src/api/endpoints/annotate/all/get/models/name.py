from pydantic import BaseModel


class NameAnnotationSuggestion(BaseModel):
    name: str
    suggestion_id: int