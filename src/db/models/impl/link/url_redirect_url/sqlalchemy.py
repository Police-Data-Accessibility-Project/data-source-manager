from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import Mapped

from src.db.models.helpers import url_id_column
from src.db.models.mixins import CreatedAtMixin, UpdatedAtMixin
from src.db.models.templates_.base import Base


class LinkURLRedirectURL(
    Base,
    CreatedAtMixin,
    UpdatedAtMixin
):
    __tablename__ = "link_urls_redirect_url"
    __table_args__ = (
        PrimaryKeyConstraint("source_url_id", "destination_url_id"),
    )

    source_url_id: Mapped[int] = url_id_column()
    destination_url_id: Mapped[int] = url_id_column()

