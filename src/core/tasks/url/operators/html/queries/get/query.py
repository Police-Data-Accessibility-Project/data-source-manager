from sqlalchemy import RowMapping, Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.html.queries.helpers import has_non_errored_urls_without_html_data
from src.db.models.impl import LinkBatchURL
from src.db.models.impl.url.core.pydantic.info import URLInfo
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.materialized_views.url_status.sqlalchemy import URLStatusMaterializedView
from src.db.queries.base.builder import QueryBuilderBase
from src.db.statement_composer import StatementComposer


class GetPendingURLsWithoutHTMLDataQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[URLInfo]:
        query = (
            has_non_errored_urls_without_html_data()
            .limit(100)
            .order_by(URL.id)
        )

        mappings: Sequence[RowMapping] = await self.sh.mappings(session, query)

        final_results: list[URLInfo] = []
        for mapping in mappings:
            url_info = URLInfo(
                id=mapping[URL.id],
                url=mapping["full_url"],
            )
            final_results.append(url_info)

        return final_results
