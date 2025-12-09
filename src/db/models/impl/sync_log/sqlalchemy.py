from sqlalchemy import PrimaryKeyConstraint, Column, Integer, DateTime

from src.db.models.helpers import enum_column
from src.db.models.impl.sync_log.enums import ResourceType, SyncType
from src.db.models.templates_.base import Base


class SyncLog(Base):
    __tablename__ = 'sync_log'
    __table_args__ = (
        PrimaryKeyConstraint('resource_type', 'sync_type', 'created_at'),
    )

    resource_type = enum_column(ResourceType, name='resource_type_enum')
    sync_type = enum_column(SyncType, name='sync_type_enum')
    count = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False)