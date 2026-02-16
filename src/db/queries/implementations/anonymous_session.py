from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.anon_session.sqlalchemy import AnonymousSession
from src.db.queries.base.builder import QueryBuilderBase


class MakeAnonymousSessionQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> UUID:
        return await self.sh.add(
            session=session,
            model=AnonymousSession(),
            return_id=True
        )
