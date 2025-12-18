from sqlalchemy import PrimaryKeyConstraint

from src.db.models.mixins import URLDependentMixin, AgencyDependentMixin, CreatedAtMixin, AnonymousSessionMixin
from src.db.models.templates_.base import Base


class AnonymousAnnotationAgency(
    Base,
    URLDependentMixin,
    AgencyDependentMixin,
    CreatedAtMixin,
    AnonymousSessionMixin
):
    __tablename__ = "annotation__anon__agency"
    __table_args__ = (
        PrimaryKeyConstraint("session_id", "url_id", "agency_id"),
    )