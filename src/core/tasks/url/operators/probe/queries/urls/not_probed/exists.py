from datetime import timedelta, datetime

from sqlalchemy import select, or_
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
            .outerjoin(
                URLWebMetadata,
                URL.id == URLWebMetadata.url_id
            )
            .where(
                or_(
                    URLWebMetadata.url_id.is_(None),
                    URLWebMetadata.updated_at < datetime.now() - timedelta(days=30)
                ),
                no_url_task_error(TaskType.PROBE_URL)
            )
        )
        return await sh.has_results(session, query=query)
