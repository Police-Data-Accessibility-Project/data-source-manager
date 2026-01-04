from typing import Sequence

from sqlalchemy import select, exists, RowMapping, func
from sqlalchemy.dialects.postgresql import aggregate_order_by
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.url.get.dto import GetURLsResponseInfo, GetURLsResponseErrorInfo, GetURLsResponseInnerInfo
from src.db.client.helpers import add_standard_limit_and_offset
from src.db.models.impl import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.scrape_info.sqlalchemy import URLScrapeInfo
from src.db.models.impl.url.task_error.sqlalchemy import URLTaskError
from src.db.models.materialized_views.url_status.sqlalchemy import URLStatusMaterializedView
from src.db.queries.base.builder import QueryBuilderBase


class GetURLsQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        page: int,
        errors: bool
    ):
        super().__init__()
        self.page = page
        self.errors = errors

    async def run(self, session: AsyncSession) -> GetURLsResponseInfo:

        error_cte = (
            select(
                URLTaskError.url_id,
                func.array_agg(
                    aggregate_order_by(
                        func.jsonb_build_object(
                            "task_type", URLTaskError.task_type,
                            "error", URLTaskError.error,
                            "created_at", URLTaskError.created_at
                        ),
                        URLTaskError.created_at,
                    )
                ).label("error_array")
            )
            .group_by(
                URLTaskError.url_id
            )
            .cte("errors")
        )


        query = (
            select(
                URL.id,
                LinkBatchURL.batch_id,
                URL.full_url,
                URL.collector_metadata,
                URLStatusMaterializedView.status,
                URL.created_at,
                URL.updated_at,
                URL.name,
                error_cte.c.error_array
            )
            .outerjoin(
                LinkBatchURL
            )
            .outerjoin(
                URLStatusMaterializedView,
                URLStatusMaterializedView.url_id == URL.id
            )
            .outerjoin(
                error_cte,
                error_cte.c.url_id == URL.id
            )
            .outerjoin(
                URLScrapeInfo
            )
            .order_by(URL.id)
        )
        if self.errors:
            # Only return URLs with errors
            query = query.where(
                exists(
                    select(URLTaskError).where(URLTaskError.url_id == URL.id)
                )
            )
        add_standard_limit_and_offset(query, self.page)
        mappings: Sequence[RowMapping] = await self.sh.mappings(session, query)

        final_results = []
        for mapping in mappings:
            error_results = []
            error_array = mapping["error_array"] or []
            for error in error_array:
                error_result = GetURLsResponseErrorInfo(
                    task=error["task_type"],
                    error=error["error"],
                    updated_at=error["created_at"]
                )
                error_results.append(error_result)
            final_results.append(
                GetURLsResponseInnerInfo(
                    id=mapping[URL.id],
                    batch_id=mapping[LinkBatchURL.batch_id],
                    url=mapping["full_url"],
                    collector_metadata=mapping[URL.collector_metadata],
                    status=mapping[URLStatusMaterializedView.status],
                    created_at=mapping[URL.created_at],
                    updated_at=mapping[URL.updated_at],
                    errors=error_results,
                )
            )

        return GetURLsResponseInfo(
            urls=final_results,
            count=len(final_results)
        )