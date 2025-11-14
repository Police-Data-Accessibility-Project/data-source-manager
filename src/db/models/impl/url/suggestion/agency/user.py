from sqlalchemy import Column, Boolean, UniqueConstraint, Integer
from sqlalchemy.orm import relationship, Mapped

from src.db.models.helpers import get_agency_id_foreign_column
from src.db.models.mixins import URLDependentMixin
from src.db.models.templates_.with_id import WithIDBase


class UserURLAgencySuggestion(URLDependentMixin, WithIDBase):
    __tablename__ = "user_url_agency_suggestions"

    agency_id: Mapped[int] = get_agency_id_foreign_column(nullable=True)
    user_id = Column(Integer, nullable=False)
    is_new = Column(Boolean, nullable=True)

    agency = relationship("Agency")
    url = relationship("URL")

    __table_args__ = (
        UniqueConstraint("agency_id", "url_id", "user_id", name="uq_user_url_agency_suggestions"),
    )
