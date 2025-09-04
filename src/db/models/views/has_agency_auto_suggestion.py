"""
    CREATE OR REPLACE VIEW url_has_agency_auto_suggestions_view AS
    SELECT
        u.id as url_id,
        (uas.id IS NOT NULL) AS has_agency_suggestions
    FROM public.urls u
    LEFT JOIN public.url_auto_agency_id_subtasks uas on u.id = uas.url_id
"""


from sqlalchemy import Column, Boolean, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped

from src.db.models.mixins import URLDependentMixin, ViewMixin
from src.db.models.templates_.base import Base


class HasAgencyAutoSuggestionView(
    Base,
    URLDependentMixin,
    ViewMixin
):

    __tablename__ = "url_has_agency_auto_suggestions_view"
    __table_args__ = (
        PrimaryKeyConstraint("url_id"),
        {"info": "view"}
    )

    has_agency_suggestions: Mapped[bool] = Column(Boolean, nullable=False)

