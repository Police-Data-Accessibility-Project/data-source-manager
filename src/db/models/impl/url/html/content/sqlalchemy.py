from sqlalchemy import UniqueConstraint, Column, Text, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

from src.db.enums import PGEnum
from src.db.models.mixins import UpdatedAtMixin, URLDependentMixin
from src.db.models.templates_.base import Base
from src.db.models.templates_.with_id import WithIDBase


class URLHTMLContent(
    UpdatedAtMixin,
    URLDependentMixin,
    Base,
):
    __tablename__ = 'url_html_content'
    __table_args__ = (
        PrimaryKeyConstraint("url_id", "content_type"),
    )

    content_type = Column(
        PGEnum('Title', 'Description', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'Div', name='url_html_content_type'),
        nullable=False)
    content = Column(Text, nullable=False)


    # Relationships
    url = relationship("URL", back_populates="html_content")
