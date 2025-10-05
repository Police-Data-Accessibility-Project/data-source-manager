from sqlalchemy import select, or_, exists, text, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.internet_archives.probe.queries.cte import CheckURLInternetArchivesCTEContainer
from src.db.dtos.url.mapping import URLMapping
from src.db.helpers.query import not_exists_url
from src.db.models.impl.flag.checked_for_ia.sqlalchemy import FlagURLCheckedForInternetArchives
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase

from src.db.helpers.session import session_helper as sh

class GetURLsForInternetArchivesTaskQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[URLMapping]:
        cte = CheckURLInternetArchivesCTEContainer()
        query = (
            select(
                cte.url_id,
                cte.url
            )
            .limit(100)
        )

        db_mappings = await sh.mappings(session, query=query)
        return [
            URLMapping(
                url_id=mapping["url_id"],
                url=mapping["url"]
            ) for mapping in db_mappings
        ]
