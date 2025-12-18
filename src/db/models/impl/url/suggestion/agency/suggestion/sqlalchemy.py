import sqlalchemy as sa
from sqlalchemy.orm import relationship

from src.db.models.mixins import CreatedAtMixin, AgencyDependentMixin
from src.db.models.templates_.with_id import WithIDBase


class AgencyIDSubtaskSuggestion(
    WithIDBase,
    CreatedAtMixin,
    AgencyDependentMixin,
):
    __tablename__ = "annotation__auto__agency__suggestions"


    subtask_id = sa.Column(
        sa.Integer,
        sa.ForeignKey("annotation__auto__agency__subtasks.id"),
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