from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.html.queries.helpers import has_non_errored_urls_without_html_data
from src.db.queries.base.builder import QueryBuilderBase


class PendingURLsWithoutHTMLDataPrerequisitesQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> bool:
        statement = has_non_errored_urls_without_html_data()
        statement = statement.limit(1)
        scalar_result = await session.scalars(statement)
        return bool(scalar_result.first())