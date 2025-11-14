from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync_to_ds.impl.meta_urls.add.queries.cte import \
    DSAppLinkSyncMetaURLAddPrerequisitesCTEContainer
from src.db.queries.base.builder import QueryBuilderBase


class DSAppSyncMetaURLsAddPrerequisitesQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> bool:
        return await self.sh.results_exist(
            session=session,
            query=select(
                DSAppLinkSyncMetaURLAddPrerequisitesCTEContainer().url_id
            )
        )