from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.metrics.dtos.get.urls.aggregated.core import GetMetricsURLsAggregatedResponseDTO, \
    GetMetricsURLValidatedOldestPendingURL
from src.api.endpoints.metrics.urls.aggregated.query.subqueries.all import ALL_SUBQUERY
from src.api.endpoints.metrics.urls.aggregated.query.subqueries.oldest_pending_url import \
    GetOldestPendingURLQueryBuilder
from src.api.endpoints.metrics.urls.aggregated.query.subqueries.record_type import GetURLRecordTypeCountQueryBuilder
from src.api.endpoints.metrics.urls.aggregated.query.subqueries.status import GetURLStatusCountQueryBuilder
from src.api.endpoints.metrics.urls.aggregated.query.subqueries.url_type import GetURLTypeCountQueryBuilder
from src.core.enums import RecordType
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.materialized_views.url_status.enums import URLStatusViewEnum
from src.db.queries.base.builder import QueryBuilderBase


class GetURLsAggregatedMetricsQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> GetMetricsURLsAggregatedResponseDTO:

        oldest_pending_url: GetMetricsURLValidatedOldestPendingURL | None = \
            await GetOldestPendingURLQueryBuilder().run(session=session)

        status_counts: dict[URLStatusViewEnum, int] = \
            await GetURLStatusCountQueryBuilder().run(session=session)

        validated_counts: dict[URLType, int] = \
            await GetURLTypeCountQueryBuilder().run(session=session)

        record_type_counts: dict[RecordType, int] = \
            await GetURLRecordTypeCountQueryBuilder().run(session=session)

        return GetMetricsURLsAggregatedResponseDTO(
            count_urls_total=await sh.scalar(session, query=ALL_SUBQUERY),
            oldest_pending_url=oldest_pending_url,
            count_urls_status=status_counts,
            count_urls_type=validated_counts,
            count_urls_record_type=record_type_counts,
        )
