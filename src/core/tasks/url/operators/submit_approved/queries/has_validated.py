from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.submit_approved.queries.cte import VALIDATED_URLS_WITHOUT_DS_ALIAS
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase


class HasValidatedURLsQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> bool:
        query = (
            select(VALIDATED_URLS_WITHOUT_DS_ALIAS)
            .limit(1)
        )
        url: URL | None = await sh.one_or_none(session, query=query)
        return url is not None