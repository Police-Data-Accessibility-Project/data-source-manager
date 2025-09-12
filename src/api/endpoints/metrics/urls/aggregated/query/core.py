from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.metrics.dtos.get.urls.aggregated.core import GetMetricsURLsAggregatedResponseDTO
from src.api.endpoints.metrics.urls.aggregated.query.subqueries.all import ALL_SUBQUERY
from src.api.endpoints.metrics.urls.aggregated.query.subqueries.error import ERROR_SUBQUERY
from src.api.endpoints.metrics.urls.aggregated.query.subqueries.pending import PENDING_SUBQUERY
from src.api.endpoints.metrics.urls.aggregated.query.subqueries.rejected import REJECTED_SUBQUERY
from src.api.endpoints.metrics.urls.aggregated.query.subqueries.submitted import SUBMITTED_SUBQUERY
from src.api.endpoints.metrics.urls.aggregated.query.subqueries.validated import VALIDATED_SUBQUERY
from src.collectors.enums import URLStatus
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase


class GetURLsAggregatedMetricsQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> GetMetricsURLsAggregatedResponseDTO:

        oldest_pending_url_query = select(
            URL.id,
            URL.created_at
        ).where(
            URL.status == URLStatus.OK.value
        ).order_by(
            URL.created_at.asc()
        ).limit(1)

        oldest_pending_url = await session.execute(oldest_pending_url_query)
        oldest_pending_url = oldest_pending_url.one_or_none()
        if oldest_pending_url is None:
            oldest_pending_url_id = None
            oldest_pending_created_at = None
        else:
            oldest_pending_url_id = oldest_pending_url.id
            oldest_pending_created_at = oldest_pending_url.created_at

        return GetMetricsURLsAggregatedResponseDTO(
            count_urls_total=await sh.scalar(session, query=ALL_SUBQUERY),
            count_urls_pending=await sh.scalar(session, query=PENDING_SUBQUERY),
            count_urls_submitted=await sh.scalar(session, query=SUBMITTED_SUBQUERY),
            count_urls_validated=await sh.scalar(session, query=VALIDATED_SUBQUERY),
            count_urls_rejected=await sh.scalar(session, query=REJECTED_SUBQUERY),
            count_urls_errors=await sh.scalar(session, query=ERROR_SUBQUERY),
            oldest_pending_url_id=oldest_pending_url_id,
            oldest_pending_url_created_at=oldest_pending_created_at,
        )
