from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import Mapped

from src.db.models.mixins import URLDependentMixin, CreatedAtMixin
from src.db.models.templates_.base import Base
from src.util.alembic_helpers import user_id_column


class LinkUserSuggestionLocationNotFound(
    Base,
    URLDependentMixin,
    CreatedAtMixin,
):
    __tablename__ = "link_user_suggestion_location_not_found"

    user_id: Mapped[int] = user_id_column()

    __table_args__ = (
        PrimaryKeyConstraint("url_id", "user_id"),
    )