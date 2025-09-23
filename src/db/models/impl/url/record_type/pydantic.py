from src.core.enums import RecordType
from src.db.models.impl.url.record_type.sqlalchemy import URLRecordType
from src.db.templates.markers.bulk.insert import BulkInsertableModel
from src.db.templates.markers.bulk.upsert import BulkUpsertableModel


class URLRecordTypePydantic(
    BulkInsertableModel,
    BulkUpsertableModel,
):
    url_id: int
    record_type: RecordType

    @classmethod
    def sa_model(cls) -> type[URLRecordType]:
        return URLRecordType

    @classmethod
    def id_field(cls) -> str:
        return "url_id"