from typing import Sequence

from sqlalchemy import RowMapping, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync_to_ds.constants import PER_REQUEST_ENTITY_LIMIT
from src.core.tasks.scheduled.impl.sync_to_ds.impl.data_sources.add.queries.cte import \
    DSAppLinkSyncDataSourceAddPrerequisitesCTEContainer
from src.core.tasks.scheduled.impl.sync_to_ds.shared.convert import convert_sm_url_status_to_ds_url_status
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.internet_archives.probe.sqlalchemy import URLInternetArchivesProbeMetadata
from src.db.models.impl.url.optional_ds_metadata.sqlalchemy import URLOptionalDataSourceMetadata
from src.db.models.impl.url.record_type.sqlalchemy import URLRecordType
from src.db.models.impl.url.web_metadata.sqlalchemy import URLWebMetadata
from src.db.models.materialized_views.url_status.sqlalchemy import URLStatusMaterializedView
from src.db.queries.base.builder import QueryBuilderBase
from src.external.pdap.enums import DataSourcesURLStatus
from src.external.pdap.impl.sync.data_sources._shared.content import DataSourceSyncContentModel
from src.external.pdap.impl.sync.data_sources.add.request import AddDataSourcesOuterRequest, AddDataSourcesInnerRequest


class DSAppSyncDataSourcesAddGetQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> AddDataSourcesOuterRequest:
        cte = DSAppLinkSyncDataSourceAddPrerequisitesCTEContainer()

        agency_id_cte = (
            select(
                LinkURLAgency.url_id,
                func.array_agg(LinkURLAgency.agency_id).label("agency_ids")
            )
            .group_by(
                LinkURLAgency.url_id
            )
            .cte()
        )

        query = (
            select(
                cte.url_id,
                # Required
                URL.full_url,
                URL.name,
                URLWebMetadata.status_code,
                URLRecordType.record_type,
                agency_id_cte.c.agency_ids,
                # Optional
                URL.description,
                URLOptionalDataSourceMetadata.record_formats,
                URLOptionalDataSourceMetadata.data_portal_type,
                URLOptionalDataSourceMetadata.supplying_entity,
                URLOptionalDataSourceMetadata.coverage_start,
                URLOptionalDataSourceMetadata.coverage_end,
                URLOptionalDataSourceMetadata.agency_supplied,
                URLOptionalDataSourceMetadata.agency_originated,
                URLOptionalDataSourceMetadata.update_method,
                URLOptionalDataSourceMetadata.readme_url,
                URLOptionalDataSourceMetadata.originating_entity,
                URLOptionalDataSourceMetadata.retention_schedule,
                URLOptionalDataSourceMetadata.scraper_url,
                URLOptionalDataSourceMetadata.access_notes,
                URLOptionalDataSourceMetadata.access_types,
                URLInternetArchivesProbeMetadata.archive_url,
            )
            .select_from(
                cte.cte
            )
            .join(
                URL,
                URL.id == cte.url_id,
            )
            .outerjoin(
                URLOptionalDataSourceMetadata,
                URL.id == URLOptionalDataSourceMetadata.url_id,
            )
            .outerjoin(
                URLWebMetadata,
                URL.id == URLWebMetadata.url_id
            )
            .outerjoin(
                URLInternetArchivesProbeMetadata,
                URL.id == URLInternetArchivesProbeMetadata.url_id,
            )
            .join(
                URLRecordType,
                URLRecordType.url_id == URL.id,
            )
            .join(
                agency_id_cte,
                cte.url_id == agency_id_cte.c.url_id
            ).limit(PER_REQUEST_ENTITY_LIMIT)
        )

        mappings: Sequence[RowMapping] = await self.sh.mappings(
            session=session,
            query=query,
        )

        inner_requests: list[AddDataSourcesInnerRequest] = []
        for mapping in mappings:
            inner_requests.append(
                AddDataSourcesInnerRequest(
                    request_id=mapping[cte.url_id],
                    content=DataSourceSyncContentModel(
                        # Required
                        source_url=mapping["full_url"],
                        name=mapping[URL.name],
                        record_type=mapping[URLRecordType.record_type],
                        agency_ids=mapping["agency_ids"],
                        # Optional
                        description=mapping[URL.description],
                        record_formats=mapping[URLOptionalDataSourceMetadata.record_formats] or [],
                        data_portal_type=mapping[URLOptionalDataSourceMetadata.data_portal_type],
                        supplying_entity=mapping[URLOptionalDataSourceMetadata.supplying_entity],
                        coverage_start=mapping[URLOptionalDataSourceMetadata.coverage_start],
                        coverage_end=mapping[URLOptionalDataSourceMetadata.coverage_end],
                        agency_supplied=mapping[URLOptionalDataSourceMetadata.agency_supplied],
                        agency_originated=mapping[URLOptionalDataSourceMetadata.agency_originated],
                        update_method=mapping[URLOptionalDataSourceMetadata.update_method],
                        readme_url=mapping[URLOptionalDataSourceMetadata.readme_url],
                        originating_entity=mapping[URLOptionalDataSourceMetadata.originating_entity],
                        retention_schedule=mapping[URLOptionalDataSourceMetadata.retention_schedule],
                        scraper_url=mapping[URLOptionalDataSourceMetadata.scraper_url],
                        access_notes=mapping[URLOptionalDataSourceMetadata.access_notes],
                        access_types=mapping[URLOptionalDataSourceMetadata.access_types] or [],
                        # TODO: Change to convert web metadata result to URL Status
                        url_status=convert_sm_url_status_to_ds_url_status(
                            mapping[URLWebMetadata.status_code],
                        ),
                        internet_archives_url=mapping[URLInternetArchivesProbeMetadata.archive_url] or None,
                    )
                )
            )

        return AddDataSourcesOuterRequest(
            data_sources=inner_requests,
        )