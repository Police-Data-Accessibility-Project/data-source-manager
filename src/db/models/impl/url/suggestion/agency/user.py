from sqlalchemy import Column, Boolean, UniqueConstraint, Integer, PrimaryKeyConstraint
from sqlalchemy.orm import relationship, Mapped

from src.db.models.helpers import get_agency_id_foreign_column
from src.db.models.mixins import URLDependentMixin
from src.db.models.templates_.base import Base
from src.db.models.templates_.with_id import WithIDBase


class UserURLAgencySuggestion(URLDependentMixin, Base):
    __tablename__ = "user_url_agency_suggestions"
    __table_args__ = (
        PrimaryKeyConstraint("agency_id", "url_id", "user_id"),
    )

    agency_id: Mapped[int] = get_agency_id_foreign_column(nullable=True)
    user_id = Column(Integer, nullable=False)
    is_new = Column(Boolean, nullable=True)

    agency = relationship("Agency")
    url = relationship("URL")
