from sqlalchemy import Column, Text, String, JSON
from sqlalchemy.orm import relationship

from src.api.endpoints.annotate.all.get.models.name import NameAnnotationSuggestion
from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from src.db.models.helpers import enum_column
from src.db.models.impl.url.checked_for_duplicate import URLCheckedForDuplicate
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.probed_for_404 import URLProbedFor404
from src.db.models.impl.url.record_type.sqlalchemy import URLRecordType
from src.db.models.impl.url.suggestion.location.auto.subtask.sqlalchemy import AutoLocationIDSubtask
from src.db.models.impl.url.suggestion.name.sqlalchemy import URLNameSuggestion
from src.db.models.impl.url.task_error.sqlalchemy import URLTaskError
from src.db.models.mixins import UpdatedAtMixin, CreatedAtMixin
from src.db.models.templates_.with_id import WithIDBase


class URL(UpdatedAtMixin, CreatedAtMixin, WithIDBase):
    __tablename__ = 'urls'

    # The batch this URL is associated with
    url = Column(Text, unique=True)
    name = Column(String)
    description = Column(Text)
    # The metadata from the collector
    collector_metadata = Column(JSON)
    # The outcome of the URL: submitted, human_labeling, rejected, duplicate, etc.
    status = enum_column(
            URLStatus,
            name='url_status',
            nullable=False
    )

    source = enum_column(
        URLSource,
        name='url_source',
        nullable=False
    )

    # Relationships
    batch = relationship(
        "Batch",
        secondary="link_batch_urls",
        back_populates="urls",
        uselist=False,
    )
    record_type = relationship(
        URLRecordType,
        uselist=False,
    )
    duplicates = relationship("Duplicate", back_populates="original_url")
    html_content = relationship("URLHTMLContent", back_populates="url", cascade="all, delete-orphan")
    task_errors = relationship(
        URLTaskError,
        cascade="all, delete-orphan"
    )
    tasks = relationship(
        "Task",
        secondary="link_task_urls",
        back_populates="urls",
    )
    auto_agency_subtasks = relationship(
        "URLAutoAgencyIDSubtask"
    )
    auto_location_subtasks = relationship(
        AutoLocationIDSubtask
    )
    name_suggestions = relationship(
        URLNameSuggestion
    )
    user_agency_suggestions = relationship(
        "UserUrlAgencySuggestion", back_populates="url")
    auto_record_type_suggestion = relationship(
        "AutoRecordTypeSuggestion", uselist=False, back_populates="url")
    user_record_type_suggestions = relationship(
        "UserRecordTypeSuggestion", back_populates="url")
    auto_relevant_suggestion = relationship(
        "AutoRelevantSuggestion", uselist=False, back_populates="url")
    user_relevant_suggestions = relationship(
        "UserURLTypeSuggestion", back_populates="url")
    reviewing_user = relationship(
        "ReviewingUserURL", uselist=False, back_populates="url")
    optional_data_source_metadata = relationship(
        "URLOptionalDataSourceMetadata", uselist=False, back_populates="url")
    confirmed_agencies = relationship(
        "LinkURLAgency",
    )
    data_source = relationship(
        "URLDataSource",
        back_populates="url",
        uselist=False
    )
    checked_for_duplicate = relationship(
        URLCheckedForDuplicate,
        uselist=False,
        back_populates="url"
    )
    probed_for_404 = relationship(
        URLProbedFor404,
        uselist=False,
        back_populates="url"
    )
    compressed_html = relationship(
        "URLCompressedHTML",
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