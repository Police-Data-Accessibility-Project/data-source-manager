from typing import Sequence

from sqlalchemy import select, func, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.metrics.batches.aggregated.query.batch_status_.response import \
    BatchStatusCountByBatchStrategyResponseDTO
from src.collectors.enums import CollectorType
from src.core.enums import BatchStatus
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.batch.strategy.sqlalchemy import BatchStrategy
from src.db.queries.base.builder import QueryBuilderBase

from src.db.helpers.session import session_helper as sh

class BatchStatusByBatchStrategyQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[BatchStatusCountByBatchStrategyResponseDTO]:
        query = (
            select(
                BatchStrategy.name.label("strategy"),
                Batch.status,
                func.count(Batch.id).label("count")
            )
            .select_from(Batch)
            .join(
                BatchStrategy,
                Batch.batch_strategy_id == BatchStrategy.id,
            )
            .group_by(BatchStrategy.name, Batch.status)
        )
        mappings: Sequence[RowMapping] = await sh.mappings(session, query=query)

        results: list[BatchStatusCountByBatchStrategyResponseDTO] = []
        for mapping in mappings:
            results.append(
                BatchStatusCountByBatchStrategyResponseDTO(
                    strategy=CollectorType(mapping["strategy"]),
                    status=BatchStatus(mapping["status"]),
                    count=mapping["count"]
                )
            )
        return results
