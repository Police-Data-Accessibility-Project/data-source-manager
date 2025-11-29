from sqlalchemy import Column, Integer, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from src.db.models.mixins import BatchDependentMixin
from src.db.models.templates_.base import Base
from src.db.models.templates_.with_id import WithIDBase


class Duplicate(BatchDependentMixin, Base):
    """
    Identifies duplicates which occur within a batch
    """
    __tablename__ = 'duplicates'
    __table_args__ = (
        PrimaryKeyConstraint("batch_id"),
    )

    original_url_id = Column(
        Integer,
        ForeignKey('urls.id'),
        nullable=False,
        doc="The original URL ID"
    )

    # Relationships
    batch = relationship("Batch", back_populates="duplicates")
    original_url = relationship("URL", back_populates="duplicates")
