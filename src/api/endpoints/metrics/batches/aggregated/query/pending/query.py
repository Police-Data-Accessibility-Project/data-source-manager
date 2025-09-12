from typing import Sequence

from sqlalchemy import select, func, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.metrics.batches.aggregated.query.models.strategy_count import CountByBatchStrategyResponse
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.queries.base.builder import QueryBuilderBase
from src.db.helpers.session import session_helper as sh

class PendingURLCountByBatchStrategyQueryBuilder(QueryBuilderBase):
    async def run(
        self, session: AsyncSession
    ) -> list[CountByBatchStrategyResponse]:

        query = (
            select(
                Batch.strategy,
                func.count(LinkBatchURL.url_id).label("count")
            )
            .join(
                LinkBatchURL,
                LinkBatchURL.batch_id == Batch.id
            )
            .outerjoin(
                FlagURLValidated,
                FlagURLValidated.url_id == LinkBatchURL.url_id
            )
            .where(FlagURLValidated.url_id.is_(None))
            .group_by(Batch.strategy)
        )

        mappings: Sequence[RowMapping] = await sh.mappings(session, query=query)
        results = [CountByBatchStrategyResponse(**mapping) for mapping in mappings]
        return results
