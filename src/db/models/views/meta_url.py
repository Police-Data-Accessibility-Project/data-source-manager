"""
    CREATE OR REPLACE VIEW meta_url_view AS
        SELECT
            urls.id
        FROM urls
        INNER JOIN flag_url_validated fuv on fuv.url_id = urls.id
        where fuv.type = 'meta url'
"""

from sqlalchemy import PrimaryKeyConstraint

from src.db.models.mixins import ViewMixin, URLDependentMixin
from src.db.models.templates_.base import Base


class MetaURL(
    Base,
    ViewMixin,
    URLDependentMixin,
):

    __tablename__ = "meta_url_view"
    __table_args__ = (
        PrimaryKeyConstraint("url_id"),
        {"info": "view"}
    )