from typing import Sequence

from sqlalchemy import select, func, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.helpers.session import session_helper as sh
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.queries.base.builder import QueryBuilderBase


class GetURLTypeCountQueryBuilder(QueryBuilderBase):

    async def run(
        self,
        session: AsyncSession
    ) -> dict[URLType, int]:
        query = (
            select(
                FlagURLValidated.type,
                func.count(FlagURLValidated.url_id).label("count")
            )
            .group_by(
                FlagURLValidated.type
            )
        )

        mappings: Sequence[RowMapping] = await sh.mappings(session, query=query)

        return {
            mapping["type"]: mapping["count"]
            for mapping in mappings
        }