from typing import Sequence

from sqlalchemy import select, func, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync_to_ds.impl.meta_urls.add.queries.cte import \
    DSAppLinkSyncMetaURLAddPrerequisitesCTEContainer
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase
from src.external.pdap.impl.sync.meta_urls._shared.content import MetaURLSyncContentModel
from src.external.pdap.impl.sync.meta_urls.add.request import AddMetaURLsOuterRequest, AddMetaURLsInnerRequest


class DSAppSyncMetaURLsAddGetQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> AddMetaURLsOuterRequest:
        cte = DSAppLinkSyncMetaURLAddPrerequisitesCTEContainer()

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
                URL.full_url,
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
                agency_id_cte,
                cte.url_id == agency_id_cte.c.url_id
            )
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
                        url=mapping[URL.full_url],
                        agency_ids=mapping["agency_ids"]
                    )
                )
            )

        return AddMetaURLsOuterRequest(
            meta_urls=inner_requests,
        )