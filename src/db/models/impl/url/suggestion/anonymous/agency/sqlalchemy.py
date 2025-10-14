from sqlalchemy import PrimaryKeyConstraint

from src.db.models.mixins import URLDependentMixin, AgencyDependentMixin, CreatedAtMixin
from src.db.models.templates_.base import Base


class AnonymousAnnotationAgency(
    Base,
    URLDependentMixin,
    AgencyDependentMixin,
    CreatedAtMixin
):
    __tablename__ = "anonymous_annotation_agency"
    __table_args__ = (
        PrimaryKeyConstraint("url_id", "agency_id"),
    )