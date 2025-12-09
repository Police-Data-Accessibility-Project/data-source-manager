"""
    create view integrity__non_federal_agencies_no_location_view as
        select
            ag.id as agency_id
        from agencies ag
        left join link_agencies__locations link on ag.id = link.agency_id
        where ag.jurisdiction_type != 'federal'
        and link.location_id is null
    """
from sqlalchemy import String, Column, PrimaryKeyConstraint

from src.db.models.helpers import VIEW_ARG
from src.db.models.mixins import ViewMixin, AgencyDependentMixin
from src.db.models.templates_.base import Base

class IntegrityNonFederalAgenciesNoLocation(
    Base,
    ViewMixin,
    AgencyDependentMixin,
):
    __tablename__ = "integrity__non_federal_agencies_no_location_view"
    __table_args__ = (
        PrimaryKeyConstraint("agency_id"),
        VIEW_ARG,
    )

    name = Column(String)
