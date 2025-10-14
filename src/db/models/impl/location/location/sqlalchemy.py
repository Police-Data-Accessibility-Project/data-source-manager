from sqlalchemy import Float, Column

from src.db.models.helpers import us_state_column, county_column, locality_column, enum_column
from src.db.models.impl.location.location.enums import LocationType
from src.db.models.templates_.with_id import WithIDBase


class Location(
    WithIDBase
):

    __tablename__ = "locations"

    state_id = us_state_column(nullable=True)
    county_id = county_column(nullable=True)
    locality_id = locality_column(nullable=True)
    type = enum_column(LocationType, name="location_type", nullable=False)
    lat = Column(Float(), nullable=True)
    lng = Column(Float(), nullable=True)
