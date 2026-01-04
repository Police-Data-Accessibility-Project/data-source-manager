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
from sqlalchemy import Column, String, Integer

from src.db.models.helpers import enum_column
from src.db.models.impl.location.location.enums import LocationType
from src.db.models.mixins import ViewMixin, LocationDependentMixin
from src.db.models.templates_.with_id import WithIDBase


class LocationExpandedView(
    WithIDBase,
    ViewMixin,
):

    __tablename__ = "locations_expanded"
    __table_args__ = (
        {"info": "view"}
    )

    type = enum_column(LocationType, name="location_type", nullable=False)
    state_name = Column(String)
    state_iso = Column(String)
    county_name = Column(String)
    county_fips = Column(String)
    locality_name = Column(String)
    locality_id = Column(Integer)
    state_id = Column(Integer)
    county_id = Column(Integer)
    display_name = Column(String)
    full_display_name = Column(String)
