from sqlalchemy import delete, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.internet_archives.probe.queries.cte import CheckURLInternetArchivesCTEContainer
from src.db.models.impl.flag.checked_for_ia.sqlalchemy import FlagURLCheckedForInternetArchives
from src.db.queries.base.builder import QueryBuilderBase

class DeleteOldUnsuccessfulIACheckedFlagsQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> None:
        cte = CheckURLInternetArchivesCTEContainer()
        query = (
            delete(FlagURLCheckedForInternetArchives)
            .where(
                exists(
                    select(cte.url_id)
                    .where(
                        FlagURLCheckedForInternetArchives.url_id == cte.url_id,
                    )
                )
            )
        )

        await session.execute(query)