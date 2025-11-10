from typing import Sequence

from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync_to_ds.impl.data_sources.delete.queries.cte import \
    DSAppLinkSyncDataSourceDeletePrerequisitesCTEContainer
from src.db.queries.base.builder import QueryBuilderBase


class DSAppSyncDataSourcesDeleteGetQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[int]:
        """Get DS App links to delete."""
        cte = DSAppLinkSyncDataSourceDeletePrerequisitesCTEContainer()

        query = (
            select(
                cte.ds_data_source_id,
            )
        )

        mappings: Sequence[RowMapping] = await self.sh.mappings(
            session=session,
            query=query,
        )

        return [mapping[cte.ds_data_source_id] for mapping in mappings]