from sqlalchemy import text, Column

from src.db.models.mixins import CreatedAtMixin
from src.db.models.templates_.base import Base
from sqlalchemy.dialects.postgresql import UUID


class AnonymousSession(
    Base,
    CreatedAtMixin
):
    __tablename__ = "anonymous_sessions"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )