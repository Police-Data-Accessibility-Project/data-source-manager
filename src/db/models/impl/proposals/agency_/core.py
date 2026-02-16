from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, relationship

from src.db.models.helpers import enum_column
from src.db.models.impl.agency.enums import JurisdictionType, AgencyType
from src.db.models.impl.proposals.enums import ProposalStatus
from src.db.models.mixins import CreatedAtMixin
from src.db.models.templates_.with_id import WithIDBase


class ProposalAgency(
    WithIDBase,
    CreatedAtMixin
):

    __tablename__ = "proposal__agencies"

    name = Column(String, nullable=False)
    agency_type: Mapped[AgencyType] = enum_column(AgencyType, name="agency_type_enum")
    jurisdiction_type: Mapped[JurisdictionType] = enum_column(
        JurisdictionType,
        name="jurisdiction_type_enum",
        nullable=False,
    )
    proposing_user_id: Mapped[int | None] = Column(Integer, nullable=True)
    proposal_status: Mapped[ProposalStatus] = enum_column(ProposalStatus, name="proposal_status_enum")
    promoted_agency_id: Mapped[int | None] = Column(
        Integer,
        ForeignKey("agencies.id"),
        nullable=True
    )

    locations = relationship(
        "LocationExpandedView",
        primaryjoin="ProposalAgency.id == ProposalLinkAgencyLocation.proposal_agency_id",
        secondaryjoin="LocationExpandedView.id == ProposalLinkAgencyLocation.location_id",
        secondary="proposal__link__agencies__locations",
    )
