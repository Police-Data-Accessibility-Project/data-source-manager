"""
Provides decision information on an Agency

"""
from sqlalchemy import Column, Integer, String, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped

from src.db.models.mixins import CreatedAtMixin
from src.db.models.templates_.base import Base


class ProposalAgencyDecisionInfo(
    Base,
    CreatedAtMixin,
):
    __tablename__ = "proposal__agencies__decision_info"
    __table_args__ = (
        PrimaryKeyConstraint("proposal_agency_id"),
    )

    proposal_agency_id: Mapped[int] = Column(
        Integer,
        ForeignKey("proposal__agencies.id"),
        nullable=False
    )
    deciding_user_id: Mapped[int] = Column(Integer)
    rejection_reason: Mapped[str | None] = Column(String, nullable=True)
