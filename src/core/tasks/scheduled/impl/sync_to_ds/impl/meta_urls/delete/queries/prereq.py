from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync_to_ds.impl.meta_urls.delete.queries.cte import \
    DSAppLinkSyncMetaURLDeletePrerequisitesCTEContainer
from src.db.queries.base.builder import QueryBuilderBase


class DSAppSyncMetaURLsDeletePrerequisitesQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> bool:
        return await self.sh.results_exist(
            session=session,
            query=select(
                DSAppLinkSyncMetaURLDeletePrerequisitesCTEContainer().ds_meta_url_id
            )
        )