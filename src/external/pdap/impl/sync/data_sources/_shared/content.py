class DataSourceSyncContentModel(BaseModel):
    # Required
    source_url: str
    name: str
    record_type: RecordTypesEnum

    # Optional
    description: str | None = None

    # Optional data source metadata
    record_formats: list[str] | None = None
    data_portal_type: str | None = None
    supplying_entity: str | None = None
    coverage_start: date | None = None
    coverage_end: date | None = None
    detail_level: DetailLevel | None = None
    agency_supplied: bool | None = None
    agency_originated: bool | None = None
    agency_aggregation: AgencyAggregation | None = None
    agency_described_not_in_database: str | None = None
    update_method: UpdateMethod | None = None
    readme_url: str | None = None
    originating_entity: str | None = None
    retention_schedule: RetentionSchedule | None = None
    scraper_url: str | None = None
    access_notes: str | None = None
    access_types: list[AccessType] | None = None
    data_portal_type_other: str | None = None
    url_status: URLStatus | None = None

    agency_ids: list[int] = Field(min_length=1)
