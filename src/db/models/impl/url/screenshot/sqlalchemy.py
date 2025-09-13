from sqlalchemy import Column, LargeBinary, Integer, UniqueConstraint

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
        UniqueConstraint('url_id', name='uq_url_id_url_screenshot'),
    )


    content = Column(LargeBinary, nullable=False)
    file_size = Column(Integer, nullable=False)

