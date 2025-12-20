from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import Mapped

from src.core.enums import RecordType
from src.db.models.helpers import enum_column
from src.db.models.mixins import URLDependentMixin, CreatedAtMixin, AnonymousSessionMixin
from src.db.models.templates_.base import Base


class AnnotationRecordTypeAnon(
    Base,
    URLDependentMixin,
    CreatedAtMixin,
    AnonymousSessionMixin
):
    __tablename__ = "annotation__record_type__anon"
    __table_args__ = (
        PrimaryKeyConstraint("session_id", "url_id", "record_type"),
    )

    record_type: Mapped[RecordType] = enum_column(
        name="record_type",
        enum_type=RecordType,
    )