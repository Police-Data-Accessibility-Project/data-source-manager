from pydantic import BaseModel

class NameAnnotationSuggestion(BaseModel):
    id: int
    display_name: str
    user_count: int
    robo_count: int

class NameAnnotationResponseOuterInfo(BaseModel):
    suggestions: list[NameAnnotationSuggestion]