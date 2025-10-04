from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import override, final

from src.db.enums import TaskType
from src.db.helpers.query import not_exists_url, no_url_task_error
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.web_metadata.sqlalchemy import URLWebMetadata
from src.db.queries.base.builder import QueryBuilderBase

@final
class HasURLsWithoutProbeQueryBuilder(QueryBuilderBase):

    @override
    async def run(self, session: AsyncSession) -> bool:
        query = (
            select(
                URL.id
            )
            .where(
                not_exists_url(URLWebMetadata),
                no_url_task_error(TaskType.PROBE_URL)
            )
        )
        return await sh.has_results(session, query=query)
