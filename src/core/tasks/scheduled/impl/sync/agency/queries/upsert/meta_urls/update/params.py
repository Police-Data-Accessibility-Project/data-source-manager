from pydantic import BaseModel

from src.core.enums import RecordType
from src.db.models.impl.flag.url_validated.enums import URLValidatedType


class UpdateMetaURLsParams(BaseModel):
    validation_type: URLValidatedType | None
    url_id: int
    record_type: RecordType | None

