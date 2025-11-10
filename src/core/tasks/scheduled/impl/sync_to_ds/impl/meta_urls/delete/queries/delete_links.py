from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.url.ds_meta_url.sqlalchemy import DSAppLinkMetaURL
from src.db.queries.base.builder import QueryBuilderBase


class DSAppSyncMetaURLsDeleteRemoveLinksQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        ds_meta_url_ids: list[int]
    ):
        super().__init__()
        self._ds_meta_url_ids = ds_meta_url_ids

    async def run(self, session: AsyncSession) -> None:
        statement = (
            delete(DSAppLinkMetaURL)
            .where(DSAppLinkMetaURL.ds_meta_url_id.in_(self._ds_meta_url_ids))
        )
        await session.execute(statement)