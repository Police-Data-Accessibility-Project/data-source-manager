from typing import Sequence

from sqlalchemy import select, func, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.helpers.session import session_helper as sh
from src.db.models.views.url_status.core import URLStatusMatView
from src.db.models.views.url_status.enums import URLStatusViewEnum
from src.db.queries.base.builder import QueryBuilderBase


class GetURLStatusCountQueryBuilder(QueryBuilderBase):

    async def run(
        self,
        session: AsyncSession
    ) -> dict[URLStatusViewEnum, int]:

        query = (
            select(
                URLStatusMatView.status,
                func.count(
                    URLStatusMatView.url_id
                ).label("count")
            )
            .group_by(
                URLStatusMatView.status
            )
        )

        mappings: Sequence[RowMapping] = await sh.mappings(session, query=query)

        return {
            URLStatusViewEnum(mapping["status"]): mapping["count"]
            for mapping in mappings
        }
