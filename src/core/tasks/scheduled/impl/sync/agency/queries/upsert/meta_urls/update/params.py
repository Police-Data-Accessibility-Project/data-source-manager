from pydantic import BaseModel

from src.core.enums import RecordType
from src.db.models.impl.flag.url_validated.enums import URLType


class UpdateMetaURLsParams(BaseModel):
    validation_type: URLType | None
    url_id: int
    record_type: RecordType | None

