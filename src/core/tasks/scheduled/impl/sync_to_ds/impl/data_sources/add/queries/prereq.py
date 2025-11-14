from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync_to_ds.impl.data_sources.add.queries.cte import \
    DSAppLinkSyncDataSourceAddPrerequisitesCTEContainer
from src.db.queries.base.builder import QueryBuilderBase


class DSAppSyncDataSourcesAddPrerequisitesQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> bool:
        return await self.sh.results_exist(
            session=session,
            query=select(
                DSAppLinkSyncDataSourceAddPrerequisitesCTEContainer().url_id
            )
        )