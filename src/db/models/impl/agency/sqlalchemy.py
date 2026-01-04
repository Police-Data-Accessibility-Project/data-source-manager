"""
References an agency in the data sources database.
"""

from sqlalchemy import Column, String
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

    name = Column(String, nullable=False)
    agency_type: Mapped[AgencyType] = enum_column(AgencyType, name="agency_type_enum")
    jurisdiction_type: Mapped[JurisdictionType] = enum_column(
        JurisdictionType,
        name="jurisdiction_type_enum",
        nullable=False,
    )

    # Relationships
    automated_suggestions = relationship("AnnotationAgencyAutoSuggestion")
    user_suggestions = relationship("AnnotationAgencyUser", back_populates="agency")
    confirmed_urls = relationship("LinkURLAgency", back_populates="agency")

    locations = relationship(
        "LocationExpandedView",
        primaryjoin="Agency.id == LinkAgencyLocation.agency_id",
        secondaryjoin="LocationExpandedView.id == LinkAgencyLocation.location_id",
        secondary="link_agencies__locations",
    )
