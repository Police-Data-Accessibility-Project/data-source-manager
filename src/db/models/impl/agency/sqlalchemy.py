"""
References an agency in the data sources database.
"""

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship

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

    agency_id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    agency_type = enum_column(AgencyType, name="agency_type_enum")
    jurisdiction_type = enum_column(
        JurisdictionType,
        name="jurisdiction_type_enum",
        nullable=True,
    )

    # Relationships
    automated_suggestions = relationship("AgencyIDSubtaskSuggestion")
    user_suggestions = relationship("UserUrlAgencySuggestion", back_populates="agency")
    confirmed_urls = relationship("LinkURLAgency", back_populates="agency")
