from pydantic import BaseModel

from src.core.enums import RecordType



class RecordTypeAnnotationSuggestion(BaseModel):
    record_type: RecordType
    endorsement_count: int


