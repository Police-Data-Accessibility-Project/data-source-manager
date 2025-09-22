from sqlalchemy import Column, UniqueConstraint, Integer
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship, Mapped

from src.db.models.helpers import enum_column
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.mixins import UpdatedAtMixin, CreatedAtMixin, URLDependentMixin
from src.db.models.templates_.with_id import WithIDBase


class UserURLTypeSuggestion(
    UpdatedAtMixin,
    CreatedAtMixin,
    URLDependentMixin,
    WithIDBase
):
    __tablename__ = "user_url_type_suggestions"

    user_id = Column(Integer, nullable=False)
    type: Mapped[URLType | None] = enum_column(
        URLType,
        name="url_type",
        nullable=True
    )

    __table_args__ = (
        UniqueConstraint("url_id", "user_id", name="uq_user_relevant_suggestions"),
    )

    # Relationships

    url = relationship("URL", back_populates="user_relevant_suggestions")
