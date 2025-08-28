from pydantic import BaseModel

from src.core.enums import RecordType
from src.db.models.impl.flag.url_validated.enums import URLValidatedType


class MetaURLLookupResponse(BaseModel):
    url: str
    url_id: int | None
    record_type: RecordType | None
    validation_type: URLValidatedType | None

    @property
    def exists_in_db(self) -> bool:
        return self.url_id is not None

    @property
    def is_meta_url(self) -> bool:
        return self.record_type == RecordType.CONTACT_INFO_AND_AGENCY_META

    @property
    def is_validated(self) -> bool:
        return self.validation_type is not None