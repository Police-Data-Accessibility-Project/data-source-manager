from sqlalchemy import Column, Integer, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped

from src.db.models.mixins import URLDependentMixin
from src.db.models.templates_.base import Base


class LinkURLNewAgencySuggestion(
    Base,
    URLDependentMixin,
):

    __tablename__ = 'link_url_new_agency_suggestion'

    suggestion_id: Mapped[int] = Column(Integer, ForeignKey('new_agency_suggestions.id'), nullable=False)

    __table_args__ = (
        PrimaryKeyConstraint('url_id', 'suggestion_id'),
    )
