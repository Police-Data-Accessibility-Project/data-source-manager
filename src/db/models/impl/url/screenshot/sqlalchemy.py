from sqlalchemy import Column, LargeBinary, Integer, UniqueConstraint, PrimaryKeyConstraint

from src.db.models.helpers import url_id_primary_key_constraint
from src.db.models.mixins import URLDependentMixin, CreatedAtMixin, UpdatedAtMixin
from src.db.models.templates_.base import Base


class URLScreenshot(
    Base,
    URLDependentMixin,
    CreatedAtMixin,
    UpdatedAtMixin,
):
    __tablename__ = "url_screenshot"
    __table_args__ = (
        url_id_primary_key_constraint(),
    )


    content = Column(LargeBinary, nullable=False)
    file_size = Column(Integer, nullable=False)

