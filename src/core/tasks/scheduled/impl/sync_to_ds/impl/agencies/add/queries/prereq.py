from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync_to_ds.impl.agencies.add.queries.cte import \
    DSAppLinkSyncAgencyAddPrerequisitesCTEContainer
from src.db.queries.base.builder import QueryBuilderBase


class DSAppSyncAgenciesAddPrerequisitesQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> bool:
        return await self.sh.results_exist(
            session=session,
            query=select(
                DSAppLinkSyncAgencyAddPrerequisitesCTEContainer().agency_id
            )
        )