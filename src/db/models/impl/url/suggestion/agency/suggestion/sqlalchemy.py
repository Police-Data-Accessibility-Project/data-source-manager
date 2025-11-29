import sqlalchemy as sa
from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from src.db.models.mixins import CreatedAtMixin, AgencyDependentMixin
from src.db.models.templates_.base import Base


class AgencyIDSubtaskSuggestion(
    Base,
    CreatedAtMixin,
    AgencyDependentMixin,
):
    __tablename__ = "agency_id_subtask_suggestions"
    __table_args__ = (
        PrimaryKeyConstraint("agency_id", "subtask_id"),
    )

    subtask_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("url_auto_agency_id_subtasks.id"),
        nullable=False
    )
    confidence = sa.Column(
        sa.Integer,
        sa.CheckConstraint(
            "confidence BETWEEN 0 and 100"
        ),
        nullable=False,
    )

    agency = relationship("Agency", viewonly=True)