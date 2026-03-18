"""
    create view integrity__federal_agencies_wrong_location_view as
        with national_location as (
            select id
            from locations
            where type = 'National'
            limit 1
        )
        select
            ag.id as agency_id
        from agencies ag
        inner join link_agencies__locations link on ag.id = link.agency_id
        cross join national_location nl
        where ag.jurisdiction_type = 'federal'
        group by ag.id, nl.id
        having array_agg(link.location_id order by link.location_id) != array[nl.id::integer]
"""
from sqlalchemy import PrimaryKeyConstraint

from src.db.models.helpers import VIEW_ARG
from src.db.models.mixins import AgencyDependentMixin, ViewMixin
from src.db.models.templates_.base import Base


class IntegrityFederalAgenciesWrongLocation(
    Base,
    ViewMixin,
    AgencyDependentMixin
):
    __tablename__ = "integrity__federal_agencies_wrong_location_view"
    __table_args__ = (
        PrimaryKeyConstraint("agency_id"),
        VIEW_ARG,
    )
