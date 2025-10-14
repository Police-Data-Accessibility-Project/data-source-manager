from typing import Any

from sqlalchemy import delete, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.url.screenshot.sqlalchemy import URLScreenshot
from src.db.queries.base.builder import QueryBuilderBase


class DeleteStaleScreenshotsQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> Any:

        statement = (
            delete(
                URLScreenshot
            )
            .where(
                exists(
                    select(
                        FlagURLValidated
                    )
                    .where(
                        FlagURLValidated.url_id == URLScreenshot.url_id,
                    )
                )
            )
        )

        await session.execute(statement)