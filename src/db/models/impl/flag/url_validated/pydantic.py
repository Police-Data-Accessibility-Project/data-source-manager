from src.db.models.impl.flag.url_validated.enums import URLValidatedType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.templates.markers.bulk.insert import BulkInsertableModel
from src.db.templates.markers.bulk.upsert import BulkUpsertableModel

type_ = type

class FlagURLValidatedPydantic(
    BulkInsertableModel,
    BulkUpsertableModel
):

    url_id: int
    type: URLValidatedType

    @classmethod
    def sa_model(cls) -> type_[FlagURLValidated]:
        return FlagURLValidated

    @classmethod
    def id_field(cls) -> str:
        return "url_id"