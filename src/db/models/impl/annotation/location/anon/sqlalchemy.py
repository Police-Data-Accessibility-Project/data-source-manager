from sqlalchemy import PrimaryKeyConstraint

from src.db.models.mixins import LocationDependentMixin, URLDependentMixin, CreatedAtMixin, AnonymousSessionMixin
from src.db.models.templates_.base import Base


class AnnotationLocationAnon(
    Base,
    URLDependentMixin,
    LocationDependentMixin,
    CreatedAtMixin,
    AnonymousSessionMixin
):

    __tablename__ = "annotation__location__anon"
    __table_args__ = (
        PrimaryKeyConstraint("session_id", "url_id", "location_id"),
    )