from sqlalchemy.orm import Mapped

from src.db.models.mixins import URLDependentViewMixin
from src.db.models.templates_.base import Base


class URLHealthMaterializedView(
    Base,
    URLDependentViewMixin
):
    __tablename__ = "url_health_view"

    health: Mapped[str]
    code: Mapped[int]
    status_code: Mapped[int | None]
    redirect_url_id: Mapped[int | None]
    redirect_url: Mapped[str | None]
    redirect_status_code: Mapped[int | None]
    has_redirect: Mapped[bool]
    redirect_is_healthy: Mapped[bool]
    has_archive: Mapped[bool]
    archive_url: Mapped[str | None]
