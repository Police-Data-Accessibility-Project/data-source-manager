from src.db.models.mixins import CreatedAtMixin, URLDependentMixin, LocationDependentMixin
from src.db.models.templates_.base import Base


class UserLocationSuggestion(
    Base,
    CreatedAtMixin,
    LocationDependentMixin,
    URLDependentMixin
):
    __tablename__ = 'user_location_suggestions'