from sqlalchemy import ForeignKey, Integer, Column

from src.db.models.mixins import CreatedAtMixin
from src.db.models.templates_.base import Base


class FlagDSDeleteDataSource(
    Base,
    CreatedAtMixin
):
    __tablename__ = "flag_ds_delete_data_source"

    ds_data_source_id = Column(
        Integer,
        ForeignKey(
            "ds_app_link_data_source.ds_data_source_id",
            ondelete="CASCADE"
        ),
        primary_key=True,
    )