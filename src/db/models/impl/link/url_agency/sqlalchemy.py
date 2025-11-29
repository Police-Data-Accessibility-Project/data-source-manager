from sqlalchemy import UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import relationship, Mapped

from src.db.models.helpers import get_agency_id_foreign_column
from src.db.models.mixins import URLDependentMixin
from src.db.models.templates_.base import Base
from src.db.models.templates_.with_id import WithIDBase


class LinkURLAgency(URLDependentMixin, WithIDBase):
    __tablename__ = "link_agencies__urls"
    __table_args__ = (
        UniqueConstraint("url_id", "agency_id"),
    )

    agency_id: Mapped[int] = get_agency_id_foreign_column()

    url = relationship("URL")
    agency = relationship("Agency")

