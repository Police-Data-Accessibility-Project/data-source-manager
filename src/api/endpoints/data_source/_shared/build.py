from sqlalchemy import Select, select, and_
from sqlalchemy.orm import selectinload

from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.optional_ds_metadata.sqlalchemy import URLOptionalDataSourceMetadata
from src.db.models.impl.url.record_type.sqlalchemy import URLRecordType


def build_data_source_get_query() -> Select:
    return (
        select(
            URL,
            URL.id,
            URL.url,

            # Required Attributes
            URL.name,
            URLRecordType.record_type,

            # Optional Attributes
            URL.description,
            LinkBatchURL.batch_id,
            URLOptionalDataSourceMetadata.record_formats,
            URLOptionalDataSourceMetadata.data_portal_type,
            URLOptionalDataSourceMetadata.supplying_entity,
            URLOptionalDataSourceMetadata.coverage_start,
            URLOptionalDataSourceMetadata.coverage_end,
            URLOptionalDataSourceMetadata.agency_supplied,
            URLOptionalDataSourceMetadata.agency_aggregation,
            URLOptionalDataSourceMetadata.agency_described_not_in_database,
            URLOptionalDataSourceMetadata.agency_originated,
            URLOptionalDataSourceMetadata.update_method,
            URLOptionalDataSourceMetadata.readme_url,
            URLOptionalDataSourceMetadata.originating_entity,
            URLOptionalDataSourceMetadata.retention_schedule,
            URLOptionalDataSourceMetadata.scraper_url,
            URLOptionalDataSourceMetadata.submission_notes,
            URLOptionalDataSourceMetadata.access_notes,
            URLOptionalDataSourceMetadata.access_types
        )
        .join(
            URLRecordType,
            URLRecordType.url_id == URL.id
        )
        .join(
            FlagURLValidated,
            and_(
                FlagURLValidated.url_id == URL.id,
                FlagURLValidated.type == URLType.DATA_SOURCE
            )
        )
        .outerjoin(
            LinkBatchURL,
            LinkBatchURL.url_id == URL.id
        )
        .outerjoin(
            URLOptionalDataSourceMetadata,
            URLOptionalDataSourceMetadata.url_id == URL.id
        )
        .options(
            selectinload(URL.confirmed_agencies),
        )
    )