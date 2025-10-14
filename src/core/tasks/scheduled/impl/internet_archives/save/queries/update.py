from sqlalchemy import update, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.url.internet_archives.save.sqlalchemy import URLInternetArchivesSaveMetadata
from src.db.queries.base.builder import QueryBuilderBase


class UpdateInternetArchivesSaveMetadataQueryBuilder(QueryBuilderBase):

    def __init__(self, url_ids: list[int]):
        super().__init__()
        self.url_ids = url_ids

    async def run(self, session: AsyncSession) -> None:
        stmt = (
            update(URLInternetArchivesSaveMetadata)
            .where(URLInternetArchivesSaveMetadata.url_id.in_(self.url_ids))
            .values(last_uploaded_at=func.now())
        )
        await session.execute(stmt)

