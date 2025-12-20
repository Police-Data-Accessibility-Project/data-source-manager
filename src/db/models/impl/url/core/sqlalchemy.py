from sqlalchemy import Column, Text, String, JSON, case, literal, Boolean
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, Mapped

from src.collectors.enums import URLStatus
from src.db.models.helpers import enum_column
from src.db.models.impl.annotation.agency.auto.subtask.sqlalchemy import AnnotationAgencyAutoSubtask
from src.db.models.impl.annotation.agency.user.sqlalchemy import AnnotationAgencyUser
from src.db.models.impl.annotation.location.auto.subtask.sqlalchemy import AnnotationLocationAutoSubtask
from src.db.models.impl.annotation.location.user.sqlalchemy import AnnotationLocationUser
from src.db.models.impl.annotation.name.suggestion.sqlalchemy import AnnotationNameSuggestion
from src.db.models.impl.link.user_suggestion_not_found.location.sqlalchemy import LinkUserSuggestionLocationNotFound
from src.db.models.impl.url.checked_for_duplicate import URLCheckedForDuplicate
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.html.compressed.sqlalchemy import URLCompressedHTML
from src.db.models.impl.url.record_type.sqlalchemy import URLRecordType
from src.db.models.impl.annotation.record_type.auto.sqlalchemy import AnnotationAutoRecordType
from src.db.models.impl.annotation.record_type.user.user import AnnotationRecordTypeUser
from src.db.models.impl.annotation.url_type.auto.sqlalchemy import AnnotationAutoURLType
from src.db.models.impl.annotation.url_type.user.sqlalchemy import AnnotationURLTypeUser
from src.db.models.impl.url.task_error.sqlalchemy import URLTaskError
from src.db.models.mixins import UpdatedAtMixin, CreatedAtMixin
from src.db.models.templates_.with_id import WithIDBase


class URL(UpdatedAtMixin, CreatedAtMixin, WithIDBase):
    __tablename__ = 'urls'

    # The batch this URL is associated with
    url = Column(Text, unique=True)
    scheme: Mapped[str | None] = Column(String, nullable=True)
    name = Column(String)
    description = Column(Text)
    # The metadata from the collector
    collector_metadata = Column(JSON)
    # The outcome of the URL: submitted, human_labeling, rejected, duplicate, etc.
    status: Mapped[URLStatus] = enum_column(
            URLStatus,
            name='url_status',
            nullable=False
    )
    trailing_slash = Column(Boolean, nullable=False)

    @hybrid_property
    def full_url(self) -> str:
        if self.scheme is None:
            return self.url
        url: str = f"{self.scheme}://{self.url}"
        if self.trailing_slash:
            url += "/"
        return url

    @full_url.expression
    def full_url(cls):
        return case(
                (
                    (cls.scheme != None) & (cls.trailing_slash == True),
                    (cls.scheme + literal("://") + cls.url + literal("/"))
                ),
                (
                    (cls.scheme != None) & (cls.trailing_slash == False),
                    (cls.scheme + literal("://") + cls.url)
                ),
            else_=cls.url
        )

    source: Mapped[URLSource] = enum_column(
        URLSource,
        name='url_source',
        nullable=False
    )

    # Relationships
    batch = relationship(
        "Batch",
        secondary="link_batches__urls",
        back_populates="urls",
        uselist=False,
    )
    record_type = relationship(
        URLRecordType,
        uselist=False,
    )
    duplicates = relationship("Duplicate", back_populates="original_url")
    html_content = relationship("URLHTMLContent", cascade="all, delete-orphan")
    task_errors = relationship(
        URLTaskError,
        cascade="all, delete-orphan"
    )
    tasks = relationship(
        "Task",
        secondary="link_tasks__urls",
        back_populates="urls",
    )


    name_suggestions = relationship(
        AnnotationNameSuggestion
    )
    # Location
    user_location_suggestions = relationship(
        AnnotationLocationUser
    )
    user_location_suggestion_not_found = relationship(
        LinkUserSuggestionLocationNotFound
    )
    auto_location_subtasks = relationship(
        AnnotationLocationAutoSubtask
    )

    # Agency
    user_agency_suggestions = relationship(
        AnnotationAgencyUser, back_populates="url")
    auto_agency_subtasks = relationship(
        AnnotationAgencyAutoSubtask
    )
    # Record Type
    auto_record_type_suggestion = relationship(
        AnnotationAutoRecordType, uselist=False, back_populates="url")
    user_record_type_suggestions = relationship(
        AnnotationRecordTypeUser, back_populates="url")
    # Relvant/URL Type
    auto_relevant_suggestion = relationship(
        AnnotationAutoURLType, uselist=False, back_populates="url")
    user_relevant_suggestions = relationship(
        AnnotationURLTypeUser, back_populates="url")

    reviewing_user = relationship(
        "ReviewingUserURL", uselist=False, back_populates="url")
    optional_data_source_metadata = relationship(
        "URLOptionalDataSourceMetadata", uselist=False, back_populates="url")
    confirmed_agencies = relationship(
        "Agency",
        secondary="link_agencies__urls"

    )
    data_source = relationship(
        "DSAppLinkDataSource",
        back_populates="url",
        uselist=False
    )
    checked_for_duplicate = relationship(
        URLCheckedForDuplicate,
        uselist=False,
        back_populates="url"
    )
    compressed_html = relationship(
        URLCompressedHTML,
        uselist=False,
        back_populates="url"
    )
    scrape_info = relationship(
        "URLScrapeInfo",
        uselist=False,
    )
    web_metadata = relationship(
        "URLWebMetadata",
        uselist=False,
    )