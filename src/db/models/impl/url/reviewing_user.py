from sqlalchemy import UniqueConstraint, Column, Integer, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from src.db.models.mixins import CreatedAtMixin, URLDependentMixin
from src.db.models.templates_.base import Base
from src.db.models.templates_.with_id import WithIDBase


class ReviewingUserURL(CreatedAtMixin, URLDependentMixin, Base):
    __tablename__ = 'reviewing_user_url'
    __table_args__ = (
        PrimaryKeyConstraint(
            "url_id",
        ),
    )
    user_id = Column(Integer, nullable=False)

    # Relationships
    url = relationship("URL", uselist=False, back_populates="reviewing_user")
