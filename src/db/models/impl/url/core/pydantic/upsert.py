from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.templates_.base import Base
from src.db.templates.markers.bulk.upsert import BulkUpsertableModel


class URLUpsertModel(BulkUpsertableModel):

    @classmethod
    def id_field(cls) -> str:
        return "id"

    @classmethod
    def sa_model(cls) -> type[Base]:
        """Defines the SQLAlchemy model."""
        return URL

    id: int
    name: str | None = None
    url: str | None = None
    trailing_slash: bool | None = None
