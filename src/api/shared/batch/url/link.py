from fastapi import HTTPException
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.queries.base.builder import QueryBuilderBase


class UpdateBatchURLLinkQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        batch_id: int,
        url_id: int
    ):
        super().__init__()
        self.batch_id = batch_id
        self.url_id = url_id

    async def run(self, session: AsyncSession) -> None:

        # Delete existing link if it exists
        statement = (
            delete(LinkBatchURL)
            .where(
                LinkBatchURL.url_id==self.url_id
            )
        )
        await session.execute(statement)

        # Add new link
        link = LinkBatchURL(
            batch_id=self.batch_id,
            url_id=self.url_id
        )
        session.add(link)
