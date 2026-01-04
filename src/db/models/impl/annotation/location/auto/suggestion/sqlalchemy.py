from sqlalchemy import Column, Integer, ForeignKey, Float, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped

from src.db.models.helpers import location_id_column
from src.db.models.templates_.base import Base


class AnnotationLocationAutoSuggestion(
    Base,
):

    __tablename__ = 'annotation__location__auto__suggestions'
    __table_args__ = (
        PrimaryKeyConstraint(
            'subtask_id',
            'location_id',
            name='location_id_subtask_suggestions_pk'
        ),
    )
    subtask_id = Column(
        Integer,
        ForeignKey('annotation__location__auto__subtasks.id'),
        nullable=False,
        primary_key=True,
    )
    location_id: Mapped[int] = location_id_column()
    confidence = Column(Float, nullable=False)