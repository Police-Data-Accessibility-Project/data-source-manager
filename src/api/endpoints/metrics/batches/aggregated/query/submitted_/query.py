from typing import Sequence

from sqlalchemy import select, func, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.metrics.batches.aggregated.query.models.strategy_count import CountByBatchStrategyResponse
from src.collectors.enums import CollectorType
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.data_source.sqlalchemy import DSAppLinkDataSource
from src.db.queries.base.builder import QueryBuilderBase


class CountSubmittedByBatchStrategyQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[
        CountByBatchStrategyResponse
    ]:
        query = (
            select(
                Batch.strategy,
                func.count(DSAppLinkDataSource.id).label("count")
            )
            .join(
                LinkBatchURL,
                LinkBatchURL.batch_id == Batch.id
            )
            .join(
                DSAppLinkDataSource,
                DSAppLinkDataSource.url_id == LinkBatchURL.url_id
            )
            .group_by(Batch.strategy)
        )

        mappings: Sequence[RowMapping] = await sh.mappings(session, query=query)
        results: list[CountByBatchStrategyResponse] = []
        for mapping in mappings:
            results.append(
                CountByBatchStrategyResponse(
                    strategy=CollectorType(mapping["strategy"]),
                    count=mapping["count"]
                )
            )
        return results
