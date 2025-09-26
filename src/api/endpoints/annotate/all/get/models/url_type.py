from pydantic import BaseModel

from src.db.models.impl.flag.url_validated.enums import URLType


class URLTypeAnnotationSuggestion(BaseModel):
    url_type: URLType
    endorsement_count: int
