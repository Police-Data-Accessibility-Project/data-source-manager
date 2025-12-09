from sqlalchemy import Integer, Column

from src.db.models.mixins import CreatedAtMixin, AgencyDependentMixin, LastSyncedAtMixin
from src.db.models.templates_.base import Base


class DSAppLinkAgency(
    Base,
    CreatedAtMixin,
    AgencyDependentMixin,
    LastSyncedAtMixin
):
    __tablename__ = "ds_app_link_agency"

    ds_agency_id = Column(
        Integer,
        primary_key=True,
        nullable=False
    )