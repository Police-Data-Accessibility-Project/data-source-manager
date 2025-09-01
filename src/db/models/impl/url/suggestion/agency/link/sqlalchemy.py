from src.db.models.mixins import CreatedAtMixin, AgencyDependentMixin
from src.db.models.templates_.base import Base

import sqlalchemy as sa

class LinkAgencyIDSubtaskAgencies(
    Base,
    CreatedAtMixin,
    AgencyDependentMixin,
):
    __tablename__ = "link_agency_id_subtask_agencies"

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