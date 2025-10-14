from sqlalchemy import PrimaryKeyConstraint

from src.db.models.mixins import URLDependentMixin, CreatedAtMixin
from src.db.models.templates_.base import Base


class FlagURLSuspended(
    Base,
    URLDependentMixin,
    CreatedAtMixin
):

    __tablename__ = "flag_url_suspended"

    __table_args__ = (
        PrimaryKeyConstraint("url_id"),
    )