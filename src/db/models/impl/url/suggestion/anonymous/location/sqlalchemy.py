from sqlalchemy import PrimaryKeyConstraint

from src.db.models.mixins import LocationDependentMixin, URLDependentMixin, CreatedAtMixin, AnonymousSessionMixin
from src.db.models.templates_.base import Base


class AnonymousAnnotationLocation(
    Base,
    URLDependentMixin,
    LocationDependentMixin,
    CreatedAtMixin,
    AnonymousSessionMixin
):

    __tablename__ = "annotation__anon__location"
    __table_args__ = (
        PrimaryKeyConstraint("session_id", "url_id", "location_id"),
    )