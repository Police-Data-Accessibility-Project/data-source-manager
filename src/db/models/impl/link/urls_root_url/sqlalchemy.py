from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import Mapped

from src.db.models.helpers import url_id_column
from src.db.models.mixins import URLDependentMixin, CreatedAtMixin, UpdatedAtMixin
from src.db.models.templates_.base import Base


class LinkURLRootURL(
    UpdatedAtMixin,
    CreatedAtMixin,
    URLDependentMixin,
    Base,
):
    __tablename__ = "link_urls_root_url"
    __table_args__ = (
        PrimaryKeyConstraint("url_id", "root_url_id"),
    )

    root_url_id: Mapped[int] = url_id_column()