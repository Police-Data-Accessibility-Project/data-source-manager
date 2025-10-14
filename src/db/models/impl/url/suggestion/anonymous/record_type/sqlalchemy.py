from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import Mapped

from src.core.enums import RecordType
from src.db.models.helpers import enum_column
from src.db.models.mixins import URLDependentMixin, CreatedAtMixin
from src.db.models.templates_.base import Base


class AnonymousAnnotationRecordType(
    Base,
    URLDependentMixin,
    CreatedAtMixin
):
    __tablename__ = "anonymous_annotation_record_type"
    __table_args__ = (
        PrimaryKeyConstraint("url_id", "record_type"),
    )

    record_type: Mapped[RecordType] = enum_column(
        name="record_type",
        enum_type=RecordType,
    )