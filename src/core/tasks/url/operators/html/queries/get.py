from sqlalchemy import RowMapping, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl import LinkBatchURL
from src.db.models.impl.url.core.pydantic.info import URLInfo
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.materialized_views.url_status.sqlalchemy import URLStatusMaterializedView
from src.db.queries.base.builder import QueryBuilderBase
from src.db.statement_composer import StatementComposer


class GetPendingURLsWithoutHTMLDataQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[URLInfo]:
        query = (
            StatementComposer.has_non_errored_urls_without_html_data()
            .limit(100)
            .order_by(URL.id)
        )

        mappings: Sequence[RowMapping] = await self.sh.mappings(session, query)

        final_results: list[URLInfo] = []
        for mapping in mappings:
            url_info = URLInfo(
                id=mapping[URL.id],
                batch_id=mapping[LinkBatchURL.batch_id],
                url=mapping[URL.full_url],
                collector_metadata=mapping[URL.collector_metadata],
                status=mapping[URLStatusMaterializedView.status],
                created_at=mapping[URL.created_at],
                updated_at=mapping[URL.updated_at],
                name=mapping[URL.name]
            )
            final_results.append(url_info)

        return final_results
