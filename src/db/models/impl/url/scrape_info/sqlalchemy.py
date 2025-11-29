from sqlalchemy import PrimaryKeyConstraint

from src.db.models.helpers import enum_column
from src.db.models.impl.url.scrape_info.enums import ScrapeStatus
from src.db.models.mixins import URLDependentMixin, CreatedAtMixin, UpdatedAtMixin
from src.db.models.templates_.base import Base


class URLScrapeInfo(
    Base,
    CreatedAtMixin,
    UpdatedAtMixin,
    URLDependentMixin
):

    __tablename__ = 'url_scrape_info'
    __table_args__ = (
        PrimaryKeyConstraint("url_id"),
    )

    status = enum_column(
        enum_type=ScrapeStatus,
        name='scrape_status',
    )