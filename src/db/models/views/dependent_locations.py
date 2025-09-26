"""
create view dependent_locations(parent_location_id, dependent_location_id) as
SELECT
    lp.id AS parent_location_id,
    ld.id AS dependent_location_id
FROM
    locations lp
        JOIN locations ld ON ld.state_id = lp.state_id AND ld.type = 'County'::location_type AND lp.type = 'State'::location_type
UNION ALL
SELECT
    lp.id AS parent_location_id,
    ld.id AS dependent_location_id
FROM
    locations lp
        JOIN locations ld ON ld.county_id = lp.county_id AND ld.type = 'Locality'::location_type AND lp.type = 'County'::location_type
UNION ALL
SELECT
    lp.id AS parent_location_id,
    ld.id AS dependent_location_id
FROM
    locations lp
        JOIN locations ld ON ld.state_id = lp.state_id AND ld.type = 'Locality'::location_type AND lp.type = 'State'::location_type
UNION ALL
SELECT
    lp.id AS parent_location_id,
    ld.id AS dependent_location_id
FROM
    locations lp
        JOIN locations ld ON lp.type = 'National'::location_type AND (ld.type = ANY
                                                                      (ARRAY ['State'::location_type, 'County'::location_type, 'Locality'::location_type]));
"""
from sqlalchemy import Column, Integer, ForeignKey

from src.db.models.mixins import ViewMixin
from src.db.models.templates_.base import Base


class DependentLocationView(Base, ViewMixin):

    __tablename__ = "dependent_locations"
    __table_args__ = (
        {"info": "view"}
    )

    parent_location_id = Column(
        Integer,
        ForeignKey("locations.id"),
        primary_key=True,
    )
    dependent_location_id = Column(
        Integer,
        ForeignKey("locations.id"),
        primary_key=True
    )
