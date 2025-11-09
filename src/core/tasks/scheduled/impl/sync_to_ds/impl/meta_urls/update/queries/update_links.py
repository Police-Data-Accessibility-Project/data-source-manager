from sqlalchemy.ext.asyncio import AsyncSession

from src.db.queries.base.builder import QueryBuilderBase


class DSAppSyncMetaURLsUpdateAlterLinksQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        ds_meta_url_ids: list[int]
    ):
        super().__init__()
        self._ds_meta_url_ids = ds_meta_url_ids

    async def run(self, session: AsyncSession) -> None:
        raise NotImplementedError