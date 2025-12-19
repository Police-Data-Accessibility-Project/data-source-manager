from sqlalchemy import Column, Integer, ForeignKey

from src.db.models.mixins import CreatedAtMixin
from src.db.models.templates_.base import Base


class LinkUserNameSuggestion(
    Base,
    CreatedAtMixin,
):

    __tablename__ = "annotation__name__user__endorsements"

    suggestion_id = Column(
        Integer,
        ForeignKey("annotation__name__suggestions.id"),
        primary_key=True,
        nullable=False,
    )

    user_id = Column(
        Integer,
        primary_key=True,
        nullable=False,
    )