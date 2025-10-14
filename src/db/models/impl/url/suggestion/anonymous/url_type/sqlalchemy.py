from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import Mapped

from src.db.models.helpers import enum_column
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.mixins import URLDependentMixin, CreatedAtMixin
from src.db.models.templates_.base import Base


class AnonymousAnnotationURLType(
    Base,
    URLDependentMixin,
    CreatedAtMixin
):
    __tablename__ = "anonymous_annotation_url_type"
    __table_args__ = (
        PrimaryKeyConstraint("url_id", "url_type"),
    )

    url_type: Mapped[URLType] = enum_column(
        name="url_type",
        enum_type=URLType,
    )