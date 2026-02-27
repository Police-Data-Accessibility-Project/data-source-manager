from sqlalchemy import Column, String
from sqlalchemy.orm import relationship

from src.db.models.templates_.with_id import WithIDBase


class BatchStrategy(WithIDBase):
    __tablename__ = "batch_strategies"

    name = Column(String, nullable=False, unique=True)

    batches = relationship(
        "Batch",
        back_populates="batch_strategy",
    )
