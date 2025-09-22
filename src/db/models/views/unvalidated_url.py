"""
CREATE OR REPLACE VIEW unvalidated_url_view AS
select
    u.id as url_id
from
    urls u
    left join flag_url_validated fuv
              on fuv.url_id = u.id
where
    fuv.type is null
"""
from sqlalchemy import PrimaryKeyConstraint

from src.db.models.mixins import ViewMixin, URLDependentMixin
from src.db.models.templates_.base import Base


class UnvalidatedURL(
    Base,
    ViewMixin,
    URLDependentMixin,
):

    __tablename__ = "unvalidated_url_view"
    __table_args__ = (
        PrimaryKeyConstraint("url_id"),
        {"info": "view"}
    )