from datetime import date
from typing import Any, Sequence

from sqlalchemy import select, RowMapping, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.api.endpoints.data_source.get.response import DataSourceGetOuterResponse, DataSourceGetResponse
from src.core.enums import RecordType
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.optional_ds_metadata.enums import AgencyAggregationEnum, UpdateMethodEnum, \
    RetentionScheduleEnum, AccessTypeEnum
from src.db.models.impl.url.optional_ds_metadata.sqlalchemy import URLOptionalDataSourceMetadata
from src.db.models.impl.url.record_type.sqlalchemy import URLRecordType
from src.db.queries.base.builder import QueryBuilderBase


class GetDataSourceQueryBuilder(QueryBuilderBase):

    def __init__(
            self,
            page: int,
    ):
        super().__init__()
        self.page = page

    async def run(self, session: AsyncSession) -> DataSourceGetOuterResponse:
        query = (
            select(
                URL,
                URL.id,
                URL.url,

                # Required Attributes
                URL.name,
                URLRecordType.record_type,
                URL.confirmed_agencies,

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
            .limit(100)
            .offset((self.page - 1) * 100)
        )

        mappings: Sequence[RowMapping] = await self.sh.mappings(session, query=query)
        responses: list[DataSourceGetResponse] = []

        for mapping in mappings:
            url: URL = mapping[URL]
            url_id: int = mapping[URL.id]
            url_url: str = mapping[URL.url]
            url_name: str = mapping[URL.name]
            url_record_type: RecordType = mapping[URLRecordType.record_type]

            url_agency_ids: list[int] = []
            for agency in url.confirmed_agencies:
                url_agency_ids.append(agency.agency_id)

            url_description: str | None = mapping[URL.description]
            link_batch_url_batch_id: int | None = mapping[LinkBatchURL.batch_id]
            url_record_formats: list[str] | None = mapping[URLOptionalDataSourceMetadata.record_formats]
            url_data_portal_type: str | None = mapping[URLOptionalDataSourceMetadata.data_portal_type]
            url_supplying_entity: str | None = mapping[URLOptionalDataSourceMetadata.supplying_entity]
            url_coverage_start: date | None = mapping[URLOptionalDataSourceMetadata.coverage_start]
            url_coverage_end: date | None = mapping[URLOptionalDataSourceMetadata.coverage_end]
            url_agency_supplied: bool | None = mapping[URLOptionalDataSourceMetadata.agency_supplied]
            url_agency_aggregation: AgencyAggregationEnum | None = mapping[URLOptionalDataSourceMetadata.agency_aggregation]
            url_agency_originated: bool | None = mapping[URLOptionalDataSourceMetadata.agency_originated]
            url_agency_described_not_in_database: bool | None = mapping[URLOptionalDataSourceMetadata.agency_described_not_in_database]
            url_update_method: UpdateMethodEnum | None = mapping[URLOptionalDataSourceMetadata.update_method]
            url_readme_url: str | None = mapping[URLOptionalDataSourceMetadata.readme_url]
            url_originating_entity: str | None = mapping[URLOptionalDataSourceMetadata.originating_entity]
            url_retention_schedule: RetentionScheduleEnum | None = mapping[URLOptionalDataSourceMetadata.retention_schedule]
            url_scraper_url: str | None = mapping[URLOptionalDataSourceMetadata.scraper_url]
            url_submission_notes: str | None = mapping[URLOptionalDataSourceMetadata.submission_notes]
            url_access_notes: str | None = mapping[URLOptionalDataSourceMetadata.access_notes]
            url_access_types: list[AccessTypeEnum] | None = mapping[URLOptionalDataSourceMetadata.access_types]

            responses.append(
                DataSourceGetResponse(
                    url_id=url_id,
                    url=url_url,
                    name=url_name,
                    record_type=url_record_type,
                    agency_ids=url_agency_ids,
                    description=url_description,
                    batch_id=link_batch_url_batch_id,
                    record_formats=url_record_formats,
                    data_portal_type=url_data_portal_type,
                    supplying_entity=url_supplying_entity,
                    coverage_start=url_coverage_start,
                    coverage_end=url_coverage_end,
                    agency_supplied=url_agency_supplied,
                    agency_aggregation=url_agency_aggregation,
                    agency_originated=url_agency_originated,
                    agency_described_not_in_database=url_agency_described_not_in_database,
                    update_method=url_update_method,
                    readme_url=url_readme_url,
                    originating_entity=url_originating_entity,
                    retention_schedule=url_retention_schedule,
                    scraper_url=url_scraper_url,
                    submission_notes=url_submission_notes,
                    access_notes=url_access_notes,
                    access_types=url_access_types
                )
            )

        return DataSourceGetOuterResponse(
            results=responses,
        )

