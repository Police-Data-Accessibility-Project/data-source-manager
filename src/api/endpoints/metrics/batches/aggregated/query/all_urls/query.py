from typing import Sequence

from sqlalchemy import func, select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.metrics.batches.aggregated.query.models.strategy_count import CountByBatchStrategyResponse
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.batch.strategy.sqlalchemy import BatchStrategy
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.queries.base.builder import QueryBuilderBase


class CountAllURLsByBatchStrategyQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[CountByBatchStrategyResponse]:

        query = (
            select(
                BatchStrategy.name.label("strategy"),
                func.count(LinkBatchURL.url_id).label("count")
            )
            .select_from(Batch)
            .join(
                BatchStrategy,
                Batch.batch_strategy_id == BatchStrategy.id,
            )
            .join(LinkBatchURL)
            .group_by(BatchStrategy.name)
        )

        mappings: Sequence[RowMapping] = await sh.mappings(session, query=query)
        results = [CountByBatchStrategyResponse(**mapping) for mapping in mappings]
        return results
