from typing import Sequence

from sqlalchemy import select, func, desc, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.agency_identification.subtasks.models.suggestion import AgencySuggestion
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.queries.base.builder import QueryBuilderBase


class MatchAgencyQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        agency_name: str
    ):
        super().__init__()
        self.agency_name = agency_name

    async def run(self, session: AsyncSession) -> list[AgencySuggestion]:
        query = (
            select(
                Agency.id,
                func.similarity(Agency.name, self.agency_name).label("similarity")
            )
            .where(
                func.similarity(Agency.name, self.agency_name) > 0.5
            )
            .order_by(
                desc("similarity")
            )
            .limit(10)
        )
        mappings: Sequence[RowMapping] = await self.sh.mappings(
            session=session,
            query=query
        )
        return [
            AgencySuggestion(
                agency_id=mapping[Agency.id],
                confidence=int(mapping["similarity"] * 100)
            )
            for mapping in mappings
        ]