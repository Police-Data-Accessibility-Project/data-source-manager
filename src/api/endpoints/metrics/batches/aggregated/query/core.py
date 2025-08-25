from sqlalchemy import case, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import coalesce, func

from src.api.endpoints.metrics.batches.aggregated.dto import GetMetricsBatchesAggregatedResponseDTO, \
    GetMetricsBatchesAggregatedInnerResponseDTO
from src.api.endpoints.metrics.batches.aggregated.query.all_urls.query import CountAllURLsByBatchStrategyQueryBuilder
from src.api.endpoints.metrics.batches.aggregated.query.batch_status_.query import \
    BatchStatusByBatchStrategyQueryBuilder
from src.api.endpoints.metrics.batches.aggregated.query.requester_.requester import \
    GetBatchesAggregatedMetricsQueryRequester
from src.api.endpoints.metrics.batches.aggregated.query.submitted_.query import \
    CountSubmittedByBatchStrategyQueryBuilder
from src.api.endpoints.metrics.batches.aggregated.query.url_error.query import URLErrorByBatchStrategyQueryBuilder
from src.api.endpoints.metrics.batches.aggregated.query.validated_.query import \
    ValidatedURLCountByBatchStrategyQueryBuilder
from src.collectors.enums import URLStatus, CollectorType
from src.core.enums import BatchStatus
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.flag.url_validated.enums import ValidatedURLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.data_source.sqlalchemy import URLDataSource
from src.db.queries.base.builder import QueryBuilderBase
from src.db.statement_composer import StatementComposer


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