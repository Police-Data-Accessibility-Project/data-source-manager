from sqlalchemy import select, case, Column
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import coalesce

from src.api.endpoints.metrics.batches.breakdown.dto import GetMetricsBatchesBreakdownResponseDTO, \
    GetMetricsBatchesBreakdownInnerResponseDTO
from src.api.endpoints.metrics.batches.breakdown.error.cte_ import URL_ERROR_CTE
from src.api.endpoints.metrics.batches.breakdown.not_relevant.cte_ import NOT_RELEVANT_CTE
from src.api.endpoints.metrics.batches.breakdown.pending.cte_ import PENDING_CTE
from src.api.endpoints.metrics.batches.breakdown.submitted.cte_ import SUBMITTED_CTE
from src.api.endpoints.metrics.batches.breakdown.templates.cte_ import BatchesBreakdownURLCTE
from src.api.endpoints.metrics.batches.breakdown.total.cte_ import TOTAL_CTE
from src.api.endpoints.metrics.batches.breakdown.validated.cte_ import VALIDATED_CTE
from src.collectors.enums import URLStatus, CollectorType
from src.core.enums import BatchStatus
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase
from src.db.statement_composer import StatementComposer


class GetBatchesBreakdownMetricsQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        page: int
    ):
        super().__init__()
        self.page = page

    async def run(self, session: AsyncSession) -> GetMetricsBatchesBreakdownResponseDTO:
        sc = StatementComposer

        main_query = select(
            Batch.strategy,
            Batch.id,
            Batch.status,
            Batch.date_generated.label("created_at"),
        )

        all_ctes: list[BatchesBreakdownURLCTE] = [
            URL_ERROR_CTE,
            NOT_RELEVANT_CTE,
            PENDING_CTE,
            SUBMITTED_CTE,
            TOTAL_CTE,
            VALIDATED_CTE
        ]

        count_columns: list[Column] = [
            cte.count for cte in all_ctes
        ]


        count_query = select(
            Batch.id.label("batch_id"),
            *count_columns
        )
        for cte in all_ctes:
            count_query = count_query.outerjoin(
                cte.query,
                Batch.id == cte.batch_id
            )

        count_query = count_query.cte("url_count")


        query = (select(
            main_query.c.strategy,
            main_query.c.id,
            main_query.c.created_at,
            main_query.c.status,
            coalesce(count_query.c.count_total, 0).label("count_total"),
            coalesce(count_query.c.count_pending, 0).label("count_pending"),
            coalesce(count_query.c.count_submitted, 0).label("count_submitted"),
            coalesce(count_query.c.count_rejected, 0).label("count_rejected"),
            coalesce(count_query.c.count_error, 0).label("count_error"),
            coalesce(count_query.c.count_validated, 0).label("count_validated"),
        ).outerjoin(
            count_query,
            main_query.c.id == count_query.c.batch_id
        ).offset(
            (self.page - 1) * 100
        ).order_by(
            main_query.c.created_at.asc()
        ))

        raw_results = await session.execute(query)
        results = raw_results.all()
        batches: list[GetMetricsBatchesBreakdownInnerResponseDTO] = []
        for result in results:
            dto = GetMetricsBatchesBreakdownInnerResponseDTO(
                batch_id=result.id,
                strategy=CollectorType(result.strategy),
                status=BatchStatus(result.status),
                created_at=result.created_at,
                count_url_total=result.count_total,
                count_url_pending=result.count_pending,
                count_url_submitted=result.count_submitted,
                count_url_rejected=result.count_rejected,
                count_url_error=result.count_error,
                count_url_validated=result.count_validated
            )
            batches.append(dto)
        return GetMetricsBatchesBreakdownResponseDTO(
            batches=batches,
        )