from sqlalchemy import PrimaryKeyConstraint, Column, ForeignKey, Integer
from sqlalchemy.orm import Mapped

from src.db.models.mixins import LocationDependentMixin, CreatedAtMixin
from src.db.models.templates_.base import Base


class ProposalLinkAgencyLocation(
    Base,
    LocationDependentMixin,
    CreatedAtMixin
):
    __tablename__ = "proposal__link__agencies__locations"
    __table_args__ = (
        PrimaryKeyConstraint("proposal_agency_id", "location_id"),
    )

    proposal_agency_id: Mapped[int] = Column(
        Integer,
        ForeignKey("proposal__agencies.id"),
        nullable=False
    )