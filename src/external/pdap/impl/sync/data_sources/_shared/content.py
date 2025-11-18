from datetime import date

from pydantic import BaseModel, Field

from src.core.enums import RecordType
from src.db.models.impl.url.optional_ds_metadata.enums import AgencyAggregationEnum, UpdateMethodEnum, \
    RetentionScheduleEnum, AccessTypeEnum
from src.external.pdap.enums import DataSourcesURLStatus
from src.external.pdap.impl.sync.data_sources._shared.enums import DetailLevel


class DataSourceSyncContentModel(BaseModel):
    # Required
    source_url: str
    name: str
    record_type: RecordType

    # Optional
    description: str | None = None

    # Optional data source metadata
    record_formats: list[str] = []
    data_portal_type: str | None = None
    supplying_entity: str | None = None
    coverage_start: date | None = None
    coverage_end: date | None = None
    detail_level: DetailLevel | None = None
    agency_supplied: bool | None = None
    agency_originated: bool | None = None
    agency_aggregation: AgencyAggregationEnum | None = None
    agency_described_not_in_database: str | None = None
    update_method: UpdateMethodEnum | None = None
    readme_url: str | None = None
    originating_entity: str | None = None
    retention_schedule: RetentionScheduleEnum | None = None
    scraper_url: str | None = None
    access_notes: str | None = None
    access_types: list[AccessTypeEnum] = []
    data_portal_type_other: str | None = None
    url_status: DataSourcesURLStatus = DataSourcesURLStatus.OK
    internet_archives_url: str | None = None

    agency_ids: list[int] = []
