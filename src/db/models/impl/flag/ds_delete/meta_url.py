from sqlalchemy import Column, Integer, ForeignKey

from src.db.models.mixins import CreatedAtMixin
from src.db.models.templates_.base import Base


class FlagDSDeleteMetaURL(
    Base,
    CreatedAtMixin
):
    __tablename__ = "flag_ds_delete_meta_url"

    ds_meta_url_id = Column(
        Integer,
        ForeignKey(
            'ds_app_link_meta_url.ds_meta_url_id',
            ondelete='CASCADE'
        ),
        primary_key=True,
    )