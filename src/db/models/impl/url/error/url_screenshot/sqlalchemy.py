from sqlalchemy import Column, String

from src.db.models.helpers import url_id_primary_key_constraint
from src.db.models.mixins import URLDependentMixin, CreatedAtMixin
from src.db.models.templates_.base import Base


class ErrorURLScreenshot(
    Base,
    URLDependentMixin,
    CreatedAtMixin,
):

    __tablename__ = "error_url_screenshot"
    __table_args__ = (
        url_id_primary_key_constraint(),
    )


    error = Column(String, nullable=False)