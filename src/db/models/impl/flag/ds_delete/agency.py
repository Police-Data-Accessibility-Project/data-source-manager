from sqlalchemy import ForeignKey, Integer, Column

from src.db.models.mixins import CreatedAtMixin
from src.db.models.templates_.base import Base


class FlagDSDeleteAgency(
    Base,
    CreatedAtMixin
):
    __tablename__ = "flag_ds_delete_agency"

    ds_agency_id = Column(
        Integer,
        ForeignKey(
            "ds_app_link_agency.ds_agency_id",
            ondelete="CASCADE"
        ),
        primary_key=True,
    )