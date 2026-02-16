from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import func

from src.api.endpoints.metrics.batches.aggregated.dto import GetMetricsBatchesAggregatedResponseDTO, \
    GetMetricsBatchesAggregatedInnerResponseDTO
from src.api.endpoints.metrics.batches.aggregated.query.requester_.requester import \
    GetBatchesAggregatedMetricsQueryRequester
from src.collectors.enums import CollectorType
from src.core.enums import BatchStatus
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.queries.base.builder import QueryBuilderBase


class GetBatchesAggregatedMetricsQueryBuilder(QueryBuilderBase):

    async def run(
        self,
        session: AsyncSession
    ) -> GetMetricsBatchesAggregatedResponseDTO:

        requester = GetBatchesAggregatedMetricsQueryRequester(session=session)

        url_error_count_dict: dict[CollectorType, int] = await requester.url_error_by_collector_strategy()
        url_pending_count_dict: dict[CollectorType, int] = await requester.pending_url_count_by_collector_strategy()
        url_submitted_count_dict: dict[CollectorType, int] = await requester.submitted_url_count_by_collector_strategy()
        url_validated_count_dict: dict[CollectorType, int] = await requester.validated_url_count_by_collector_strategy()
        url_rejected_count_dict: dict[CollectorType, int] = await requester.rejected_url_count_by_collector_strategy()
        url_total_count_dict: dict[CollectorType, int] = await requester.url_count_by_collector_strategy()
        batch_status_count_dict:  dict[
            CollectorType,
            dict[BatchStatus, int]
        ] = await requester.batch_status_by_collector_strategy()





        d: dict[CollectorType, GetMetricsBatchesAggregatedInnerResponseDTO] = {}
        for collector_type in CollectorType:
            inner_response = GetMetricsBatchesAggregatedInnerResponseDTO(
                count_successful_batches=batch_status_count_dict[collector_type][BatchStatus.READY_TO_LABEL],
                count_failed_batches=batch_status_count_dict[collector_type][BatchStatus.ERROR],
                count_urls=url_total_count_dict[collector_type],
                count_urls_pending=url_pending_count_dict[collector_type],
                count_urls_validated=url_validated_count_dict[collector_type],
                count_urls_submitted=url_submitted_count_dict[collector_type],
                count_urls_rejected=url_rejected_count_dict[collector_type],
                count_urls_errors=url_error_count_dict[collector_type],
            )
            d[collector_type] = inner_response

        total_batch_query = await session.execute(
            select(
                func.count(Batch.id, label="count")
            )
        )
        total_batch_count = total_batch_query.scalars().one_or_none()
        if total_batch_count is None:
            total_batch_count = 0

        return GetMetricsBatchesAggregatedResponseDTO(
            total_batches=total_batch_count,
            by_strategy=d
        )