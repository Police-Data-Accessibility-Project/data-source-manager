from sqlalchemy import Column, Integer, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped

from src.db.models.mixins import URLDependentMixin, CreatedAtMixin
from src.db.models.templates_.base import Base


class LinkUserSubmittedURL(
    Base,
    URLDependentMixin,
    CreatedAtMixin,
):
    __tablename__ = "link_user_submitted_url"
    __table_args__ = (
        PrimaryKeyConstraint("url_id", "user_id"),
        UniqueConstraint("url_id"),
    )

    user_id: Mapped[int]