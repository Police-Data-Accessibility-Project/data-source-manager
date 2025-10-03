from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.submit_meta_urls.queries.cte import SubmitMetaURLsPrerequisitesCTEContainer
from src.db.queries.base.builder import QueryBuilderBase
from src.db.helpers.session import session_helper as sh


class MeetsMetaURLSSubmissionPrerequisitesQueryBuilder(QueryBuilderBase):


    async def run(self, session: AsyncSession) -> bool:
        cte = SubmitMetaURLsPrerequisitesCTEContainer()
        query = (
            select(
                cte.url_id,
            )
        )

        return await sh.has_results(session, query=query)