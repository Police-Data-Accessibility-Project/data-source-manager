from typing import Sequence

from sqlalchemy import select, Row
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.tasks.url.operators.record_type.queries.cte import RecordTypeTaskPrerequisiteCTEContainer
from src.db.dto_converter import DTOConverter
from src.db.dtos.url.with_html import URLWithHTML
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase


class GetRecordTypeTaskURLsQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[URLWithHTML]:
        cte = RecordTypeTaskPrerequisiteCTEContainer()
        query = (
            select(
                URL
            )
            .join(
                cte.cte,
                cte.url_id == URL.id
            )
            .options(
                selectinload(URL.html_content)
            )
            .limit(100)
            .order_by(URL.id)
        )
        urls: Sequence[Row[URL]] = await self.sh.scalars(
            session=session,
            query=query
        )
        return DTOConverter.url_list_to_url_with_html_list(urls)
