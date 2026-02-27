from datetime import date

from pydantic import BaseModel

from src.core.enums import RecordType
from src.db.models.impl.url.optional_ds_metadata.enums import AgencyAggregationEnum, UpdateMethodEnum, \
    RetentionScheduleEnum, AccessTypeEnum
from src.db.models.materialized_views.url_health.enums import URLHealthViewEnum


class DataSourceURLHealthResponse(BaseModel):
    value: URLHealthViewEnum
    code: int
    http_status_code: int | None = None
    redirect_url_id: int | None = None
    redirect_url: str | None = None
    redirect_http_status_code: int | None = None
    has_redirect: bool = False
    redirect_is_healthy: bool = False
    has_archive: bool = False
    archive_url: str | None = None


class DataSourceGetResponse(BaseModel):
    url_id: int
    url: str

    # Required Attributes
    name: str
    record_type: RecordType
    agency_ids: list[int]

    # Optional Attributes
    batch_id: int | None
    description: str | None

    # Optional data source metadata
    record_formats: list[str]
    data_portal_type: str | None = None
    supplying_entity: str | None = None
    coverage_start: date | None = None
    coverage_end: date | None = None
    agency_supplied: bool | None = None
    agency_originated: bool | None = None
    agency_aggregation: AgencyAggregationEnum | None = None
    agency_described_not_in_database: str | None = None
    update_method: UpdateMethodEnum | None = None
    readme_url: str | None = None
    originating_entity: str | None = None
    retention_schedule: RetentionScheduleEnum | None = None
    scraper_url: str | None = None
    submission_notes: str | None = None
    access_notes: str | None = None
    access_types: list[AccessTypeEnum]
    url_health: DataSourceURLHealthResponse | None = None

class DataSourceGetOuterResponse(BaseModel):
    results: list[DataSourceGetResponse]
