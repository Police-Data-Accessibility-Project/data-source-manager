from typing import Sequence

from sqlalchemy import select, Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.tasks.url.operators.auto_relevant.models.tdo import URLRelevantTDO
from src.core.tasks.url.operators.auto_relevant.queries.cte import AutoRelevantPrerequisitesCTEContainer
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase
from src.db.utils.compression import decompress_html


class GetAutoRelevantTDOsQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[URLRelevantTDO]:
        cte = AutoRelevantPrerequisitesCTEContainer()
        query = (
            select(cte.url_alias)
            .options(
                selectinload(cte.url_alias.compressed_html)
            )
        )

        query = query.limit(100).order_by(cte.url_alias.id)
        raw_result = await session.execute(query)
        urls: Sequence[Row[URL]] = raw_result.unique().scalars().all()
        tdos = []
        for url in urls:
            tdos.append(
                URLRelevantTDO(
                    url_id=url.id,
                    html=decompress_html(url.compressed_html.compressed_html),
                )
            )

        return tdos

