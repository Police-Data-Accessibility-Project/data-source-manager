from sqlalchemy import PrimaryKeyConstraint, ForeignKey, Integer, Column

from src.db.models.mixins import CreatedAtMixin, AnonymousSessionMixin
from src.db.models.templates_.base import Base


class LinkAnonymousSessionNameSuggestion(
    Base,
    AnonymousSessionMixin,
    CreatedAtMixin
):
    __tablename__ = "link__anonymous_sessions__name_suggestions"
    suggestion_id = Column(
        Integer,
        ForeignKey("url_name_suggestions.id"),
        primary_key=True,
        nullable=False,
    )
    __table_args__ = (
        PrimaryKeyConstraint(
            "session_id",
            "suggestion_id"
        ),
    )