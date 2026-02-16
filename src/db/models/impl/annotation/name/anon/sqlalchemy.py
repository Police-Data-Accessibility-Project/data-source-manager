from sqlalchemy import PrimaryKeyConstraint, ForeignKey, Integer, Column

from src.db.models.mixins import CreatedAtMixin, AnonymousSessionMixin
from src.db.models.templates_.base import Base


class AnnotationNameAnonEndorsement(
    Base,
    AnonymousSessionMixin,
    CreatedAtMixin
):
    __tablename__ = "annotation__name__anon__endorsements"
    suggestion_id = Column(
        Integer,
        ForeignKey("annotation__name__suggestions.id"),
        primary_key=True,
        nullable=False,
    )
    __table_args__ = (
        PrimaryKeyConstraint(
            "session_id",
            "suggestion_id"
        ),
    )