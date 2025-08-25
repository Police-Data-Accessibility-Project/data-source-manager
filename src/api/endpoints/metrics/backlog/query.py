from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.metrics.dtos.get.backlog import GetMetricsBacklogResponseDTO, GetMetricsBacklogResponseInnerDTO
from src.db.models.impl.backlog_snapshot import BacklogSnapshot
from src.db.queries.base.builder import QueryBuilderBase


class GetBacklogMetricsQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> GetMetricsBacklogResponseDTO:
        month = func.date_trunc('month', BacklogSnapshot.created_at)

        # 1. Create a subquery that assigns row_number() partitioned by month
        monthly_snapshot_subq = (
            select(
                BacklogSnapshot.id,
                BacklogSnapshot.created_at,
                BacklogSnapshot.count_pending_total,
                month.label("month_start"),
                func.row_number()
                .over(
                    partition_by=month,
                    order_by=BacklogSnapshot.created_at.desc()
                )
                .label("row_number")
            )
            .subquery()
        )

        # 2. Filter for the top (most recent) row in each month
        stmt = (
            select(
                monthly_snapshot_subq.c.month_start,
                monthly_snapshot_subq.c.created_at,
                monthly_snapshot_subq.c.count_pending_total
            )
            .where(monthly_snapshot_subq.c.row_number == 1)
            .order_by(monthly_snapshot_subq.c.month_start)
        )

        raw_result = await session.execute(stmt)
        results = raw_result.all()
        final_results = []
        for result in results:
            final_results.append(
                GetMetricsBacklogResponseInnerDTO(
                    month=result.month_start.strftime("%B %Y"),
                    count_pending_total=result.count_pending_total,
                )
            )

        return GetMetricsBacklogResponseDTO(entries=final_results)