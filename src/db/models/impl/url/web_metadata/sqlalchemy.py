from sqlalchemy import Column, Text, Boolean, Integer, PrimaryKeyConstraint

from src.db.models.mixins import URLDependentMixin, CreatedAtMixin, UpdatedAtMixin
from src.db.models.templates_.base import Base


class URLWebMetadata(
    Base,
    URLDependentMixin,
    CreatedAtMixin,
    UpdatedAtMixin
):
    """Contains information about the web page."""
    __tablename__ = "url_web_metadata"
    __table_args__ = (
        PrimaryKeyConstraint("url_id"),
    )

    accessed = Column(
        Boolean(),
        nullable=False
    )
    status_code = Column(
        Integer(),
        nullable=True
    )
    content_type = Column(
        Text(),
        nullable=True
    )
    error_message = Column(
        Text(),
        nullable=True
    )


