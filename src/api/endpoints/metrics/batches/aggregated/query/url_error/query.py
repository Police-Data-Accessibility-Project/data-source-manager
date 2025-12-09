from typing import Sequence

from sqlalchemy import select, func, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.metrics.batches.aggregated.query.models.strategy_count import CountByBatchStrategyResponse
from src.collectors.enums import URLStatus
from src.db.helpers.query import exists_url
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.task_error.sqlalchemy import URLTaskError
from src.db.queries.base.builder import QueryBuilderBase


class URLErrorByBatchStrategyQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[CountByBatchStrategyResponse]:
        query = (
            select(
                Batch.strategy,
                func.count(URL.id).label("count")
            )
            .select_from(Batch)
            .join(LinkBatchURL)
            .join(URL)
            .where(
                exists_url(URLTaskError)
            )
            .group_by(Batch.strategy, URL.status)
        )

        mappings: Sequence[RowMapping] = await sh.mappings(session, query=query)
        results = [CountByBatchStrategyResponse(**mapping) for mapping in mappings]
        return results


