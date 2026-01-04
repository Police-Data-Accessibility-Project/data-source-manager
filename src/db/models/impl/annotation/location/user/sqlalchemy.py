from sqlalchemy import Integer, Column, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from src.db.models.impl.link.user_suggestion_not_found.location.sqlalchemy import LinkUserSuggestionLocationNotFound
from src.db.models.mixins import CreatedAtMixin, URLDependentMixin, LocationDependentMixin
from src.db.models.templates_.base import Base


class AnnotationLocationUser(
    Base,
    CreatedAtMixin,
    LocationDependentMixin,
    URLDependentMixin
):
    __tablename__ = 'annotation__location__user'
    __table_args__ = (
        PrimaryKeyConstraint('url_id', 'location_id', 'user_id'),
    )

    user_id = Column(
        Integer,
        nullable=False,
    )

