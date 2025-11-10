from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync_to_ds.impl.agencies.delete.queries.cte import \
    DSAppLinkSyncAgencyDeletePrerequisitesCTEContainer
from src.db.queries.base.builder import QueryBuilderBase


class DSAppSyncAgenciesDeletePrerequisitesQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> bool:
        return await self.sh.results_exist(
            session=session,
            query=select(
                DSAppLinkSyncAgencyDeletePrerequisitesCTEContainer().ds_agency_id
            )
        )