from sqlalchemy import Column, ARRAY, String, Date, Boolean, Enum, PrimaryKeyConstraint
from sqlalchemy.orm import relationship, Mapped

from src.db.models.helpers import enum_column
from src.db.models.impl.url.optional_ds_metadata.enums import AgencyAggregationEnum, AccessTypeEnum, \
    RetentionScheduleEnum, UpdateMethodEnum
from src.db.models.mixins import URLDependentMixin, UpdatedAtMixin
from src.db.models.templates_.base import Base


class URLOptionalDataSourceMetadata(
    URLDependentMixin,
    Base,
    UpdatedAtMixin
):
    __tablename__ = 'url_optional_data_source_metadata'
    __table_args__ = (
        PrimaryKeyConstraint("url_id"),
    )

    record_formats = Column(ARRAY(String), nullable=False, default=[])
    data_portal_type = Column(String, nullable=True)
    supplying_entity = Column(String, nullable=True)
    coverage_start = Column(Date, nullable=True)
    coverage_end = Column(Date, nullable=True)
    agency_supplied = Column(Boolean, nullable=True)
    agency_originated = Column(Boolean, nullable=True)
    agency_aggregation: Mapped[AgencyAggregationEnum] = enum_column(AgencyAggregationEnum, name="agency_aggregation_enum")
    agency_described_not_in_database = Column(String, nullable=True)
    update_method: Mapped[UpdateMethodEnum] = enum_column(UpdateMethodEnum, name="update_method_enum")
    readme_url = Column(String, nullable=True)
    originating_entity = Column(String, nullable=True)
    retention_schedule: Mapped[RetentionScheduleEnum] = enum_column(RetentionScheduleEnum, name="retention_schedule_enum")
    scraper_url = Column(String, nullable=True)
    submission_notes = Column(String, nullable=True)
    access_notes = Column(String, nullable=True)
    access_types: Mapped[list[AccessTypeEnum]] = Column(ARRAY(
        Enum(
            AccessTypeEnum,
            name="access_type_enum",
            native_enum=True,
            values_callable=lambda AccessTypeEnum: [e.value for e in AccessTypeEnum]
        )
    ), nullable=False, default=[])
    data_portal_type_other = Column(String, nullable=True)

    # Relationships
    url = relationship("URL", uselist=False, back_populates="optional_data_source_metadata")
