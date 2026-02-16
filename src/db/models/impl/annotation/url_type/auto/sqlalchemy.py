from sqlalchemy import Column, Boolean, UniqueConstraint, String, Float, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from src.db.models.mixins import UpdatedAtMixin, CreatedAtMixin, URLDependentMixin
from src.db.models.templates_.base import Base
from src.db.models.templates_.with_id import WithIDBase


class AnnotationAutoURLType(
    UpdatedAtMixin,
    CreatedAtMixin,
    URLDependentMixin,
    Base,
):
    __tablename__ = "annotation__url_type__auto"

    relevant = Column(Boolean, nullable=True)
    confidence = Column(Float, nullable=True)
    model_name = Column(String, nullable=True)

    __table_args__ = (
        UniqueConstraint("url_id", name="auto_relevant_suggestions_uq_url_id"),
        PrimaryKeyConstraint("url_id"),
    )

    # Relationships

    url = relationship("URL")
