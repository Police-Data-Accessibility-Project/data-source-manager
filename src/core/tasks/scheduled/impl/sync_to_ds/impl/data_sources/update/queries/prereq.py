from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync_to_ds.impl.data_sources.update.queries.cte import \
    DSAppLinkSyncDataSourceUpdatePrerequisitesCTEContainer
from src.db.queries.base.builder import QueryBuilderBase


class DSAppSyncDataSourcesUpdatePrerequisitesQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> bool:
        return await self.sh.results_exist(
            session=session,
            query=select(
                DSAppLinkSyncDataSourceUpdatePrerequisitesCTEContainer().ds_data_source_id
            )
        )