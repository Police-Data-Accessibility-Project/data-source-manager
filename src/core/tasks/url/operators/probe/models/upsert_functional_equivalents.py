from pydantic import BaseModel

from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.templates_.base import Base
from src.db.templates.markers.bulk.upsert import BulkUpsertableModel


class URLFunctionalEquivalentsUpsertModel(BulkUpsertableModel):

    @classmethod
    def id_field(cls) -> str:
        return "id"

    @classmethod
    def sa_model(cls) -> type[Base]:
        """Defines the SQLAlchemy model."""
        return URL

    id: int
    url: str
    trailing_slash: bool

