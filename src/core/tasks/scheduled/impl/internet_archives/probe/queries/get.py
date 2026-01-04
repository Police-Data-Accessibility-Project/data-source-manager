from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.internet_archives.probe.queries.cte import CheckURLInternetArchivesCTEContainer
from src.db.dtos.url.mapping_.simple import SimpleURLMapping
from src.db.queries.base.builder import QueryBuilderBase

from src.db.helpers.session import session_helper as sh

class GetURLsForInternetArchivesTaskQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[SimpleURLMapping]:
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
            SimpleURLMapping(
                url_id=mapping["url_id"],
                url=mapping["url"]
            ) for mapping in db_mappings
        ]
