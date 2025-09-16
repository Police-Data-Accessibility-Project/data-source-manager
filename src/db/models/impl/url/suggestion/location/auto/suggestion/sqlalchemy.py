from sqlalchemy import Column, Integer, ForeignKey, Float

from src.db.models.helpers import location_id_column
from src.db.models.templates_.base import Base


class LocationIDSubtaskSuggestion(
    Base,
):

    __tablename__ = 'location_id_subtask_suggestions'
    subtask_id = Column(
        Integer,
        ForeignKey('auto_location_id_subtask.id'),
        nullable=False,
        primary_key=True,
    )
    location_id = location_id_column()
    confidence = Column(Float, nullable=False)