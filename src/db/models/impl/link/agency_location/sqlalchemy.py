from src.db.models.mixins import AgencyDependentMixin, LocationDependentMixin
from src.db.models.templates_.with_id import WithIDBase


class LinkAgencyLocation(
    WithIDBase,
    AgencyDependentMixin,
    LocationDependentMixin,
):
    __tablename__ = "link_agencies_locations"