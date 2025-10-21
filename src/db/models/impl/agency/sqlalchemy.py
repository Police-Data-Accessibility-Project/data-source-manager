"""
References an agency in the data sources database.
"""

from sqlalchemy import Column, Integer, String, DateTime, Sequence
from sqlalchemy.orm import relationship, Mapped

from src.db.models.helpers import enum_column
from src.db.models.impl.agency.enums import AgencyType, JurisdictionType
from src.db.models.mixins import UpdatedAtMixin, CreatedAtMixin
from src.db.models.templates_.with_id import WithIDBase


class Agency(
    CreatedAtMixin, # When agency was added to database
    UpdatedAtMixin, # When agency was last updated in database
    WithIDBase
):
    __tablename__ = "agencies"

    # TODO: Rename agency_id to ds_agency_id

    agency_id = Column(
        Integer,
        Sequence("agencies_agency_id"),
        primary_key=True)
    name = Column(String, nullable=False)
    agency_type: Mapped[AgencyType] = enum_column(AgencyType, name="agency_type_enum")
    jurisdiction_type: Mapped[JurisdictionType] = enum_column(
        JurisdictionType,
        name="jurisdiction_type_enum",
        nullable=True,
    )

    # Relationships
    automated_suggestions = relationship("AgencyIDSubtaskSuggestion")
    user_suggestions = relationship("UserUrlAgencySuggestion", back_populates="agency")
    confirmed_urls = relationship("LinkURLAgency", back_populates="agency")

    locations = relationship(
        "LocationExpandedView",
        primaryjoin="Agency.agency_id == LinkAgencyLocation.agency_id",
        secondaryjoin="LocationExpandedView.id == LinkAgencyLocation.location_id",
        secondary="link_agencies_locations",
    )
