from sqlalchemy import Column, Integer, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship

from src.db.models.mixins import UpdatedAtMixin, CreatedAtMixin, URLDependentMixin
from src.db.models.templates_.base import Base
from src.db.models.templates_.with_id import WithIDBase
from src.db.models.types import record_type_values


class AnnotationRecordTypeUser(
    UpdatedAtMixin,
    CreatedAtMixin,
    URLDependentMixin,
    Base,
):
    __tablename__ = "annotation__record_type__user"
    __table_args__ = (
        PrimaryKeyConstraint("url_id", "user_id"),
    )

    user_id = Column(Integer, nullable=False)
    record_type = Column(postgresql.ENUM(*record_type_values, name='record_type'), nullable=False)


    # Relationships
    url = relationship("URL", back_populates="user_record_type_suggestions")
