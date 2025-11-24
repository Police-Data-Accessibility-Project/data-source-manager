"""
    CREATE OR REPLACE VIEW meta_url_view AS
        SELECT
            urls.id as url_id
        FROM urls
        INNER JOIN flag_url_validated fuv on fuv.url_id = urls.id
        where fuv.type = 'meta url'
"""

from sqlalchemy import PrimaryKeyConstraint

from src.db.models.mixins import ViewMixin, URLDependentMixin, URLDependentViewMixin
from src.db.models.templates_.base import Base


class MetaURL(
    Base,
    URLDependentViewMixin
):

    __tablename__ = "meta_url_view"
