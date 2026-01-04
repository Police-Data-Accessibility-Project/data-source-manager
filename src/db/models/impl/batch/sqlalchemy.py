from sqlalchemy import Column, Integer, TIMESTAMP, Float, JSON
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship, Mapped

from src.core.enums import BatchStatus
from src.db.models.helpers import CURRENT_TIME_SERVER_DEFAULT
from src.db.models.impl.log.sqlalchemy import Log
from src.db.models.templates_.with_id import WithIDBase
from src.db.models.types import batch_status_enum


class Batch(WithIDBase):
    __tablename__ = 'batches'

    strategy = Column(
        postgresql.ENUM(
            'example',
            'ckan',
            'muckrock_county_search',
            'auto_googler',
            'muckrock_all_search',
            'muckrock_simple_search',
            'common_crawler',
            'manual',
            name='batch_strategy'),
        nullable=False)
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
