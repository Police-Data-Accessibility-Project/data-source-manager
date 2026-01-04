from typing import Sequence

from sqlalchemy import select, func, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync_to_ds.constants import PER_REQUEST_ENTITY_LIMIT
from src.core.tasks.scheduled.impl.sync_to_ds.impl.meta_urls.add.queries.cte import \
    DSAppLinkSyncMetaURLAddPrerequisitesCTEContainer
from src.core.tasks.scheduled.impl.sync_to_ds.shared.convert import convert_sm_url_status_to_ds_url_status
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.internet_archives.probe.sqlalchemy import URLInternetArchivesProbeMetadata
from src.db.models.impl.url.web_metadata.sqlalchemy import URLWebMetadata
from src.db.queries.base.builder import QueryBuilderBase
from src.external.pdap.impl.sync.meta_urls._shared.content import MetaURLSyncContentModel
from src.external.pdap.impl.sync.meta_urls.add.request import AddMetaURLsOuterRequest, AddMetaURLsInnerRequest


class DSAppSyncMetaURLsAddGetQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> AddMetaURLsOuterRequest:
        cte = DSAppLinkSyncMetaURLAddPrerequisitesCTEContainer()

        agency_id_cte = (
            select(
                LinkURLAgency.url_id,
                func.array_agg(LinkURLAgency.agency_id).label("agency_ids"),

            )
            .group_by(
                LinkURLAgency.url_id
            )
            .cte()
        )

        query = (
            select(
                cte.url_id,
                URL.full_url,
                URLWebMetadata.status_code,
                URLInternetArchivesProbeMetadata.archive_url,
                agency_id_cte.c.agency_ids
            )
            .select_from(
                cte.cte
            )
            .join(
                URL,
                URL.id == cte.url_id,
            )
            .join(
                URLWebMetadata,
                URL.id == URLWebMetadata.url_id,
            )
            .outerjoin(
                URLInternetArchivesProbeMetadata,
                URL.id == URLInternetArchivesProbeMetadata.url_id,
            )
            .join(
                agency_id_cte,
                cte.url_id == agency_id_cte.c.url_id
            )
            .limit(PER_REQUEST_ENTITY_LIMIT)
        )

        mappings: Sequence[RowMapping] = await self.sh.mappings(
            session=session,
            query=query,
        )

        inner_requests: list[AddMetaURLsInnerRequest] = []
        for mapping in mappings:
            inner_requests.append(
                AddMetaURLsInnerRequest(
                    request_id=mapping[cte.url_id],
                    content=MetaURLSyncContentModel(
                        url=mapping["full_url"],
                        agency_ids=mapping["agency_ids"],
                        internet_archives_url=mapping[URLInternetArchivesProbeMetadata.archive_url] or None,
                        url_status=convert_sm_url_status_to_ds_url_status(
                            mapping[URLWebMetadata.status_code],
                        ),
                    )
                )
            )

        return AddMetaURLsOuterRequest(
            meta_urls=inner_requests,
        )