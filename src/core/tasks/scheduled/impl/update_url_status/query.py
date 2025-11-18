from sqlalchemy import update, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.collectors.enums import URLStatus
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.web_metadata.sqlalchemy import URLWebMetadata
from src.db.queries.base.builder import QueryBuilderBase


class UpdateURLStatusQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> None:

        # Update broken URLs to nonbroken if their status is not 404
        query_broken_to_ok = (
            update(URL)
            .values(
                status=URLStatus.OK
            )
            .where(
                exists(
                    select(1).where(
                        URLWebMetadata.url_id == URL.id,  # <-- correlate
                        URLWebMetadata.status_code != 404,
                        URL.status == URLStatus.BROKEN
                    )
                )
            )
        )

        # Update ok URLs to broken if their status is 404
        query_ok_to_broken = (
            update(URL)
            .values(
                status=URLStatus.BROKEN
            )
            .where(
                exists(
                    select(1).where(
                        URLWebMetadata.url_id == URL.id,  # <-- correlate
                        URLWebMetadata.status_code == 404,
                        URL.status == URLStatus.OK
                    )
                )
            )
        )

        await session.execute(query_broken_to_ok)
        await session.execute(query_ok_to_broken)