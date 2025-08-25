
from src.api.endpoints.metrics.batches.aggregated.query.all_urls.query import CountAllURLsByBatchStrategyQueryBuilder
from src.api.endpoints.metrics.batches.aggregated.query.batch_status_.query import \
    BatchStatusByBatchStrategyQueryBuilder
from src.api.endpoints.metrics.batches.aggregated.query.batch_status_.response import \
    BatchStatusCountByBatchStrategyResponseDTO
from src.api.endpoints.metrics.batches.aggregated.query.models.strategy_count import CountByBatchStrategyResponse
from src.api.endpoints.metrics.batches.aggregated.query.pending.query import PendingURLCountByBatchStrategyQueryBuilder
from src.api.endpoints.metrics.batches.aggregated.query.rejected.query import \
    RejectedURLCountByBatchStrategyQueryBuilder
from src.api.endpoints.metrics.batches.aggregated.query.requester_.convert import \
    convert_strategy_counts_to_strategy_count_dict
from src.api.endpoints.metrics.batches.aggregated.query.submitted_.query import \
    CountSubmittedByBatchStrategyQueryBuilder
from src.api.endpoints.metrics.batches.aggregated.query.url_error.query import URLErrorByBatchStrategyQueryBuilder
from src.api.endpoints.metrics.batches.aggregated.query.validated_.query import \
    ValidatedURLCountByBatchStrategyQueryBuilder
from src.collectors.enums import CollectorType
from src.core.enums import BatchStatus
from src.db.queries.base.builder import QueryBuilderBase
from src.db.templates.requester import RequesterBase


class GetBatchesAggregatedMetricsQueryRequester(RequesterBase):

    async def _run_strategy_count_query_builder(
        self, query_builder: type[QueryBuilderBase]) -> dict[CollectorType, int]:
        responses: list[CountByBatchStrategyResponse] = \
            await query_builder().run(self.session)

        return convert_strategy_counts_to_strategy_count_dict(responses)

    async def url_error_by_collector_strategy(self) -> dict[CollectorType, int]:
        return await self._run_strategy_count_query_builder(URLErrorByBatchStrategyQueryBuilder)

    async def url_count_by_collector_strategy(self) -> dict[CollectorType, int]:
        return await self._run_strategy_count_query_builder(CountAllURLsByBatchStrategyQueryBuilder)

    async def submitted_url_count_by_collector_strategy(self) -> dict[CollectorType, int]:
        return await self._run_strategy_count_query_builder(CountSubmittedByBatchStrategyQueryBuilder)

    async def validated_url_count_by_collector_strategy(self) -> dict[CollectorType, int]:
        return await self._run_strategy_count_query_builder(ValidatedURLCountByBatchStrategyQueryBuilder)

    async def rejected_url_count_by_collector_strategy(self) -> dict[CollectorType, int]:
        return await self._run_strategy_count_query_builder(RejectedURLCountByBatchStrategyQueryBuilder)

    async def pending_url_count_by_collector_strategy(self) -> dict[CollectorType, int]:
        return await self._run_strategy_count_query_builder(PendingURLCountByBatchStrategyQueryBuilder)

    async def batch_status_by_collector_strategy(self) -> dict[
        CollectorType,
        dict[BatchStatus, int]
    ]:

        responses: list[BatchStatusCountByBatchStrategyResponseDTO] = \
            await BatchStatusByBatchStrategyQueryBuilder().run(self.session)

        result: dict[CollectorType, dict[BatchStatus, int]] = {
            collector_type: {
                BatchStatus.ERROR: 0,
                BatchStatus.READY_TO_LABEL: 0,
            }
            for collector_type in CollectorType
        }
        for response in responses:
            if response.status not in (
                BatchStatus.ERROR,
                BatchStatus.READY_TO_LABEL
            ):
                continue
            result[response.strategy][response.status] = response.count

        return result

