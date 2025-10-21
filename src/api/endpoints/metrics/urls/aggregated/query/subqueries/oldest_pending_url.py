from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.metrics.dtos.get.urls.aggregated.core import GetMetricsURLValidatedOldestPendingURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.views.url_status.core import URLStatusMatView
from src.db.models.views.url_status.enums import URLStatusViewEnum
from src.db.queries.base.builder import QueryBuilderBase

from src.db.helpers.session import session_helper as sh

class GetOldestPendingURLQueryBuilder(QueryBuilderBase):

    async def run(
        self,
        session: AsyncSession
    ) -> GetMetricsURLValidatedOldestPendingURL | None:

        query = (
            select(
                URLStatusMatView.url_id,
                URL.created_at
            )
            .join(
                URL,
                URLStatusMatView.url_id == URL.id
            ).where(
                URLStatusMatView.status.not_in(
                    [
                        URLStatusViewEnum.SUBMITTED.value,
                        URLStatusViewEnum.ACCEPTED.value,
                        URLStatusViewEnum.AWAITING_SUBMISSION.value,
                    ]
                )
            ).order_by(
                URL.created_at.asc()
            ).limit(1)
        )

        mapping: RowMapping | None = (await session.execute(query)).mappings().one_or_none()
        if mapping is None:
            return None

        return GetMetricsURLValidatedOldestPendingURL(
            url_id=mapping["url_id"],
            created_at=mapping["created_at"],
        )

