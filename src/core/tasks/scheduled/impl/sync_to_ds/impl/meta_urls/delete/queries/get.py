from typing import Sequence

from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync_to_ds.constants import PER_REQUEST_ENTITY_LIMIT
from src.core.tasks.scheduled.impl.sync_to_ds.impl.meta_urls.delete.queries.cte import \
    DSAppLinkSyncMetaURLDeletePrerequisitesCTEContainer
from src.db.queries.base.builder import QueryBuilderBase


class DSAppSyncMetaURLsDeleteGetQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[int]:
        """Get DS App links to delete."""
        cte = DSAppLinkSyncMetaURLDeletePrerequisitesCTEContainer()

        query = (
            select(
                cte.ds_meta_url_id,
            )
            .limit(PER_REQUEST_ENTITY_LIMIT)
        )

        mappings: Sequence[RowMapping] = await self.sh.mappings(
            session=session,
            query=query,
        )

        return [mapping[cte.ds_meta_url_id] for mapping in mappings]