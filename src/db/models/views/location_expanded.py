"""
create or replace view public.locations_expanded
            (id, type, state_name, state_iso, county_name, county_fips, locality_name, locality_id, state_id, county_id,
             display_name, full_display_name)
as
SELECT
    locations.id,
    locations.type,
    us_states.state_name,
    us_states.state_iso,
    counties.name   AS county_name,
    counties.fips   AS county_fips,
    localities.name AS locality_name,
    localities.id   AS locality_id,
    us_states.id    AS state_id,
    counties.id     AS county_id,
    CASE
        WHEN locations.type = 'Locality'::location_type THEN localities.name
        WHEN locations.type = 'County'::location_type THEN counties.name::character varying
        WHEN locations.type = 'State'::location_type THEN us_states.state_name::character varying
        ELSE NULL::character varying
        END         AS display_name,
    CASE
        WHEN locations.type = 'Locality'::location_type THEN concat(localities.name, ', ', counties.name, ', ',
                                                                    us_states.state_name)::character varying
        WHEN locations.type = 'County'::location_type
            THEN concat(counties.name, ', ', us_states.state_name)::character varying
        WHEN locations.type = 'State'::location_type THEN us_states.state_name::character varying
        ELSE NULL::character varying
        END         AS full_display_name
FROM
    locations
        LEFT JOIN us_states ON locations.state_id = us_states.id
        LEFT JOIN counties ON locations.county_id = counties.id
        LEFT JOIN localities ON locations.locality_id = localities.id;
"""
from sqlalchemy import PrimaryKeyConstraint

from src.db.models.helpers import enum_column
from src.db.models.impl.location.location.enums import LocationType
from src.db.models.mixins import ViewMixin, LocationDependentMixin
from src.db.models.templates_.base import Base


class LocationExpandedView(
    Base,
    ViewMixin,
    LocationDependentMixin
):


    __tablename__ = "locations_expanded"
    __table_args__ = (
        PrimaryKeyConstraint("location_id"),
        {"info": "view"}
    )

    type = enum_column(LocationType, name="location_type", nullable=False)
    # TODO: Complete later