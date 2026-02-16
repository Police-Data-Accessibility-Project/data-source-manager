from sqlalchemy import Column, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from src.db.models.mixins import URLDependentMixin, UpdatedAtMixin, CreatedAtMixin
from src.db.models.templates_.base import Base
from src.db.models.templates_.with_id import WithIDBase
from src.db.models.types import record_type_values


class AnnotationAutoRecordType(
    UpdatedAtMixin,
    CreatedAtMixin,
    URLDependentMixin,
    Base,
):
    __tablename__ = "annotation__record_type__auto"
    record_type = Column(postgresql.ENUM(*record_type_values, name='record_type'), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint("url_id"),
    )

    # Relationships

    url = relationship("URL", back_populates="auto_record_type_suggestion")


