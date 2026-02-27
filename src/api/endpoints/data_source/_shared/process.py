from sqlalchemy import RowMapping

from src.api.endpoints.data_source.get.response import DataSourceGetResponse, DataSourceURLHealthResponse
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.optional_ds_metadata.sqlalchemy import URLOptionalDataSourceMetadata
from src.db.models.impl.url.record_type.sqlalchemy import URLRecordType
from src.db.models.materialized_views.url_health.sqlalchemy import URLHealthMaterializedView


def process_data_source_get_mapping(
    mapping: RowMapping
) -> DataSourceGetResponse:
    url: URL = mapping[URL]

    url_agency_ids: list[int] = []
    for agency in url.confirmed_agencies:
        url_agency_ids.append(agency.id)

    url_health: DataSourceURLHealthResponse | None = None
    health_value = mapping[URLHealthMaterializedView.health]
    if health_value is not None:
        url_health = DataSourceURLHealthResponse(
            value=health_value,
            code=mapping[URLHealthMaterializedView.code],
            http_status_code=mapping[URLHealthMaterializedView.status_code],
            redirect_url_id=mapping[URLHealthMaterializedView.redirect_url_id],
            redirect_url=mapping[URLHealthMaterializedView.redirect_url],
            redirect_http_status_code=mapping[URLHealthMaterializedView.redirect_status_code],
            has_redirect=mapping[URLHealthMaterializedView.has_redirect] or False,
            redirect_is_healthy=mapping[URLHealthMaterializedView.redirect_is_healthy] or False,
            has_archive=mapping[URLHealthMaterializedView.has_archive] or False,
            archive_url=mapping[URLHealthMaterializedView.archive_url] or None,
        )

    return DataSourceGetResponse(
        url_id=mapping[URL.id],
        url=mapping[URL.url],
        name=mapping[URL.name],
        record_type=mapping[URLRecordType.record_type],
        agency_ids=url_agency_ids,
        description=mapping[URL.description],
        batch_id=mapping[LinkBatchURL.batch_id],
        record_formats=mapping[URLOptionalDataSourceMetadata.record_formats] or [],
        data_portal_type=mapping[URLOptionalDataSourceMetadata.data_portal_type],
        supplying_entity=mapping[URLOptionalDataSourceMetadata.supplying_entity],
        coverage_start=mapping[URLOptionalDataSourceMetadata.coverage_start],
        coverage_end=mapping[URLOptionalDataSourceMetadata.coverage_end],
        agency_supplied=mapping[URLOptionalDataSourceMetadata.agency_supplied],
        agency_aggregation=mapping[URLOptionalDataSourceMetadata.agency_aggregation],
        agency_originated=mapping[URLOptionalDataSourceMetadata.agency_originated],
        agency_described_not_in_database=mapping[URLOptionalDataSourceMetadata.agency_described_not_in_database],
        update_method=mapping[URLOptionalDataSourceMetadata.update_method],
        readme_url=mapping[URLOptionalDataSourceMetadata.readme_url],
        originating_entity=mapping[URLOptionalDataSourceMetadata.originating_entity],
        retention_schedule=mapping[URLOptionalDataSourceMetadata.retention_schedule],
        scraper_url=mapping[URLOptionalDataSourceMetadata.scraper_url],
        submission_notes=mapping[URLOptionalDataSourceMetadata.submission_notes],
        access_notes=mapping[URLOptionalDataSourceMetadata.access_notes],
        access_types=mapping[URLOptionalDataSourceMetadata.access_types] or [],
        url_health=url_health,
    )
