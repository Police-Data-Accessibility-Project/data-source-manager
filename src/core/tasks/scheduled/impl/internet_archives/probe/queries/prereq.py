from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.internet_archives.probe.queries.cte import CheckURLInternetArchivesCTEContainer
from src.db.helpers.query import not_exists_url
from src.db.models.impl.flag.checked_for_ia.sqlalchemy import FlagURLCheckedForInternetArchives
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase

from src.db.helpers.session import session_helper as sh

class CheckURLInternetArchivesTaskPrerequisitesQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> bool:
        cte = CheckURLInternetArchivesCTEContainer()
        query = (
            select(cte.url_id)
        )
        return await sh.results_exist(session, query=query)
