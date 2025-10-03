from typing import Any, Sequence

from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.submit_meta_urls.queries.cte import SubmitMetaURLsPrerequisitesCTEContainer
from src.db.queries.base.builder import QueryBuilderBase
from src.external.pdap.impl.meta_urls.request import SubmitMetaURLsRequest

from src.db.helpers.session import session_helper as sh

class GetMetaURLsForSubmissionQueryBuilder(QueryBuilderBase):


    async def run(self, session: AsyncSession) -> list[SubmitMetaURLsRequest]:
        cte = SubmitMetaURLsPrerequisitesCTEContainer()
        query = (
            select(
                cte.url_id,
                cte.agency_id,
                cte.url
            )
        )

        mappings: Sequence[RowMapping] = await sh.mappings(session, query=query)

        return [
            SubmitMetaURLsRequest(
                url_id=mapping["url_id"],
                agency_id=mapping["agency_id"],
                url=mapping["url"],
            )
            for mapping in mappings
        ]
