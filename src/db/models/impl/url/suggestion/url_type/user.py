from sqlalchemy import Column, UniqueConstraint, Integer, PrimaryKeyConstraint
from sqlalchemy.dialects import postgresql
from sqlalchemy.orm import relationship, Mapped

from src.db.models.helpers import enum_column
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.mixins import UpdatedAtMixin, CreatedAtMixin, URLDependentMixin
from src.db.models.templates_.base import Base
from src.db.models.templates_.with_id import WithIDBase


class UserURLTypeSuggestion(
    UpdatedAtMixin,
    CreatedAtMixin,
    URLDependentMixin,
    Base,
):
    __tablename__ = "user_url_type_suggestions"
    __table_args__ = (
        PrimaryKeyConstraint("url_id", "user_id"),
    )

    user_id = Column(Integer, nullable=False)
    type: Mapped[URLType | None] = enum_column(
        URLType,
        name="url_type",
        nullable=True
    )

    # Relationships

    url = relationship("URL", back_populates="user_relevant_suggestions")
