from sqlalchemy import Column, Integer, TIMESTAMP, Float, JSON, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from src.core.enums import BatchStatus
from src.db.models.helpers import CURRENT_TIME_SERVER_DEFAULT
from src.db.models.impl.log.sqlalchemy import Log
from src.db.models.templates_.with_id import WithIDBase
from src.db.models.types import batch_status_enum


class Batch(WithIDBase):
    __tablename__ = 'batches'

    batch_strategy_id = Column(
        Integer,
        ForeignKey("batch_strategies.id"),
        nullable=False,
        index=True,
    )
    user_id = Column(Integer, nullable=True)
    # Gives the status of the batch
    status: Mapped[BatchStatus] = Column(
        batch_status_enum,
        nullable=False
    )
    date_generated = Column(TIMESTAMP, nullable=False, server_default=CURRENT_TIME_SERVER_DEFAULT)

    # Time taken to generate the batch
    # TODO: Add means to update after execution
    compute_time = Column(Float)
    # The parameters used to generate the batch
    parameters = Column(JSON)

    # Relationships
    batch_strategy = relationship(
        "BatchStrategy",
        back_populates="batches",
        lazy="joined",
    )
    urls = relationship(
        "URL",
        secondary="link_batches__urls",
        back_populates="batch",
        overlaps="url"
    )
    # These relationships exist but are never referenced by their attributes
    # missings = relationship("Missing", back_populates="batch")
    logs = relationship(Log, back_populates="batch")
    duplicates = relationship("Duplicate", back_populates="batch")

    @property
    def strategy(self) -> str | None:
        if self.batch_strategy is None:
            return None
        return self.batch_strategy.name
