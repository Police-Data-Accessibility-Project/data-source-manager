from sqlalchemy import PrimaryKeyConstraint

from src.db.models.mixins import AgencyDependentMixin, LocationDependentMixin
from src.db.models.templates_.base import Base


class LinkAgencyLocation(
    Base,
    AgencyDependentMixin,
    LocationDependentMixin,
):
    __tablename__ = "link_agencies__locations"
    __table_args__ = (
        PrimaryKeyConstraint("agency_id", "location_id"),
    )