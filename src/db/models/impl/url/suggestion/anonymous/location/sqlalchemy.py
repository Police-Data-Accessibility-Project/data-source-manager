from sqlalchemy import PrimaryKeyConstraint

from src.db.models.mixins import LocationDependentMixin, URLDependentMixin, CreatedAtMixin
from src.db.models.templates_.base import Base


class AnonymousAnnotationLocation(
    Base,
    URLDependentMixin,
    LocationDependentMixin,
    CreatedAtMixin
):

    __tablename__ = "anonymous_annotation_location"
    __table_args__ = (
        PrimaryKeyConstraint("url_id", "location_id"),
    )