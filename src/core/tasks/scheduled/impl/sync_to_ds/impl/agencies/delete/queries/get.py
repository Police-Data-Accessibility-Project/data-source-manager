from typing import Sequence

from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync_to_ds.constants import PER_REQUEST_ENTITY_LIMIT
from src.core.tasks.scheduled.impl.sync_to_ds.impl.agencies.delete.queries.cte import \
    DSAppLinkSyncAgencyDeletePrerequisitesCTEContainer
from src.db.queries.base.builder import QueryBuilderBase


class DSAppSyncAgenciesDeleteGetQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[int]:
        """Get DS App links to delete."""
        cte = DSAppLinkSyncAgencyDeletePrerequisitesCTEContainer()

        query = (
            select(
                cte.ds_agency_id,
            ).limit(PER_REQUEST_ENTITY_LIMIT)
        )

        mappings: Sequence[RowMapping] = await self.sh.mappings(
            session=session,
            query=query,
        )

        return [mapping[cte.ds_agency_id] for mapping in mappings]