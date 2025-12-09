from typing import ClassVar

from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, event

from src.db.models.exceptions import WriteToViewError
from src.db.models.helpers import get_created_at_column, CURRENT_TIME_SERVER_DEFAULT, url_id_primary_key_constraint, \
    VIEW_ARG
from sqlalchemy.dialects.postgresql import UUID


class URLDependentMixin:
    url_id = Column(
        Integer,
        ForeignKey(
            'urls.id',
            ondelete="CASCADE",
        ),
        nullable=False
    )


class TaskDependentMixin:
    task_id = Column(
        Integer,
        ForeignKey(
            'tasks.id',
            ondelete="CASCADE",
        ),
        nullable=False
    )


class BatchDependentMixin:
    batch_id = Column(
        Integer,
        ForeignKey(
            'batches.id',
            ondelete="CASCADE",
        ),
        nullable=False
    )

class LocationDependentMixin:
    location_id = Column(
        Integer,
        ForeignKey(
            'locations.id',
            ondelete="CASCADE",
        ),
        nullable=False
    )

class AgencyDependentMixin:
    agency_id = Column(
        Integer,
        ForeignKey(
            'agencies.id',
            ondelete="CASCADE",
        ),
        nullable=False
    )

class CreatedAtMixin:
    created_at = get_created_at_column()

class LastSyncedAtMixin:
    last_synced_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=CURRENT_TIME_SERVER_DEFAULT
    )


class UpdatedAtMixin:
    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=CURRENT_TIME_SERVER_DEFAULT,
        onupdate=CURRENT_TIME_SERVER_DEFAULT
    )

class ViewMixin:
    """Attach to any mapped class that represents a DB view."""
    __is_view__: ClassVar[bool] = True

    @classmethod
    def __declare_last__(cls) -> None:
        # Block writes on this mapped class
        for evt in ("before_insert", "before_update", "before_delete"):
            event.listen(cls, evt, cls._block_write)

    @staticmethod
    def _block_write(mapper, connection, target):
        raise WriteToViewError(f"{type(target).__name__} is a read-only view.")

class URLDependentViewMixin(URLDependentMixin, ViewMixin):
    __table_args__ = (
        url_id_primary_key_constraint(),
        VIEW_ARG
    )

class AnonymousSessionMixin:
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            'anonymous_sessions.id',
            ondelete="CASCADE",
        ),
        nullable=False
    )