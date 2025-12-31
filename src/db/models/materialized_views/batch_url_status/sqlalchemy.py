from sqlalchemy.orm import Mapped

from src.db.models.mixins import ViewMixin, BatchDependentMixin
from src.db.models.templates_.base import Base


class BatchURLStatusMaterializedView(
    Base,
    ViewMixin,
    BatchDependentMixin
):

    __tablename__ = "batch_url_status_mat_view"
    batch_url_status: Mapped[str]