from sqlalchemy import PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from src.db.models.mixins import CreatedAtMixin, URLDependentMixin
from src.db.models.templates_.base import Base


class URLCheckedForDuplicate(CreatedAtMixin, URLDependentMixin, Base):
    __tablename__ = 'url_checked_for_duplicate'
    __table_args__ = (PrimaryKeyConstraint("url_id"),)

    # Relationships
    url = relationship("URL", uselist=False, back_populates="checked_for_duplicate")
