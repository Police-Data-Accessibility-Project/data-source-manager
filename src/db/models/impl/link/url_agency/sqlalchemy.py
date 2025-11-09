from sqlalchemy import UniqueConstraint
from sqlalchemy.orm import relationship, Mapped

from src.db.models.helpers import get_agency_id_foreign_column
from src.db.models.mixins import URLDependentMixin
from src.db.models.templates_.with_id import WithIDBase


class LinkURLAgency(URLDependentMixin, WithIDBase):
    __tablename__ = "link_urls_agency"

    agency_id: Mapped[int] = get_agency_id_foreign_column()

    url = relationship("URL")
    agency = relationship("Agency")

    __table_args__ = (
        UniqueConstraint("url_id", "agency_id", name="uq_confirmed_url_agency"),
    )
