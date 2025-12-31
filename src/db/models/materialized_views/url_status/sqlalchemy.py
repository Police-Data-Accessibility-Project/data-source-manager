from sqlalchemy.orm import Mapped

from src.db.models.mixins import URLDependentViewMixin
from src.db.models.templates_.base import Base


class URLStatusMaterializedView(
    Base,
    URLDependentViewMixin
):

    __tablename__ = "url_status_mat_view"

    status: Mapped[str]
    code: Mapped[int]