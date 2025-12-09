from src.db.models.mixins import URLDependentViewMixin
from src.db.models.templates_.base import Base


class HTMLDuplicateURLMaterializedView(
    Base,
    URLDependentViewMixin
):
    __tablename__ = "mat_view__html_duplicate_url"