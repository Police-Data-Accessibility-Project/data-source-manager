from sqlalchemy import String, Column

from src.db.models.helpers import enum_column
from src.db.models.impl.agency.enums import JurisdictionType, AgencyType
from src.db.models.mixins import CreatedAtMixin, LocationDependentMixin
from src.db.models.templates_.with_id import WithIDBase


class NewAgencySuggestion(
    WithIDBase,
    CreatedAtMixin,
    LocationDependentMixin,
):

    __tablename__ = 'new_agency_suggestions'

    name = Column(String)
    jurisdiction_type = enum_column(JurisdictionType, name='jurisdiction_type_enum', nullable=True)
    agency_type = enum_column(AgencyType, name='agency_type_enum', nullable=True)