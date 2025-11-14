from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync_to_ds.impl.data_sources.delete.queries.cte import \
    DSAppLinkSyncDataSourceDeletePrerequisitesCTEContainer
from src.db.queries.base.builder import QueryBuilderBase


class DSAppSyncDataSourcesDeletePrerequisitesQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> bool:
        return await self.sh.results_exist(
            session=session,
            query=select(
                DSAppLinkSyncDataSourceDeletePrerequisitesCTEContainer().ds_data_source_id
            )
        )