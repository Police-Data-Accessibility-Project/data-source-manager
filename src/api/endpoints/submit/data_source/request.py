from datetime import date

from src.api.shared.models.request_base import RequestBase
from src.core.enums import RecordType
from src.db.models.impl.url.optional_ds_metadata.enums import AgencyAggregationEnum, UpdateMethodEnum, \
    RetentionScheduleEnum, AccessTypeEnum


class DataSourceSubmissionRequest(RequestBase):
    # Required
    name: str
    record_type: RecordType
    source_url: str

    # Optional URL DS Metadata
    coverage_start: date | None = None
    coverage_end: date | None = None
    supplying_entity: str | None = None
    agency_supplied: bool | None = None
    agency_originated: bool | None = None
    agency_aggregation: AgencyAggregationEnum | None = None
    agency_described_not_in_database: str | None = None
    data_portal_type: str | None = None
    update_method: UpdateMethodEnum | None = None
    readme_url: str | None = None
    originating_entity: str | None = None
    retention_schedule: RetentionScheduleEnum | None = None
    scraper_url: str | None = None
    submission_notes: str | None = None
    access_notes: str | None = None
    access_types: list[AccessTypeEnum] = []
    record_formats: list[str] = []

    # Links to other entities
    agency_ids: list[int] = []
    location_ids: list[int] = []
