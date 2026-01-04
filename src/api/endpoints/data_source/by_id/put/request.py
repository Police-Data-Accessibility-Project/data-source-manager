from datetime import date

from pydantic import BaseModel

from src.core.enums import RecordType
from src.db.models.impl.url.optional_ds_metadata.enums import AgencyAggregationEnum, UpdateMethodEnum, \
    RetentionScheduleEnum, AccessTypeEnum


class DataSourcePutRequest(BaseModel):

    # Required Attributes
    url: str | None = None
    name: str | None = None
    record_type: RecordType | None = None

    # Optional Attributes
    batch_id: int | None = None
    description: str | None = None

    # Optional data source metadata
    record_formats: list[str] | None = None
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
    access_types: list[AccessTypeEnum] | None = None

    def optional_data_source_metadata_not_none(self) -> bool:
        return (
            self.record_formats is not None or
            self.data_portal_type is not None or
            self.supplying_entity is not None or
            self.coverage_start is not None or
            self.coverage_end is not None or
            self.agency_supplied is not None or
            self.agency_originated is not None or
            self.agency_aggregation is not None or
            self.agency_described_not_in_database is not None or
            self.update_method is not None or
            self.readme_url is not None or
            self.originating_entity is not None or
            self.retention_schedule is not None or
            self.scraper_url is not None or
            self.submission_notes is not None or
            self.access_notes is not None or
            self.access_types is not None
        )