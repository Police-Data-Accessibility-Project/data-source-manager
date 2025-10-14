from sqlalchemy import RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.internet_archives.save.queries.shared.get_valid_entries import \
    IA_SAVE_VALID_ENTRIES_QUERY
from src.db.queries.base.builder import QueryBuilderBase
from src.db.helpers.session import session_helper as sh

class MeetsPrerequisitesForInternetArchivesSaveQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> bool:

        query = (
            IA_SAVE_VALID_ENTRIES_QUERY
            .limit(1)
        )

        result: RowMapping | None = await sh.one_or_none(session, query=query)

        return result is not None