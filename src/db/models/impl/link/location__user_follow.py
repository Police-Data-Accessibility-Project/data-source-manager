from sqlalchemy import Integer, Column, PrimaryKeyConstraint

from src.db.models.mixins import LocationDependentMixin, CreatedAtMixin
from src.db.models.templates_.base import Base


class LinkLocationUserFollow(
    Base,
    LocationDependentMixin,
    CreatedAtMixin
):
    __tablename__ = "link__locations__user_follows"
    __table_args__ = (
        PrimaryKeyConstraint(
            "user_id",
            "location_id"
        ),
    )

    user_id = Column(Integer, nullable=False)
