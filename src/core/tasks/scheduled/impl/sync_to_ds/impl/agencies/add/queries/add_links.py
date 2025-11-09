from sqlalchemy.ext.asyncio import AsyncSession

from src.db.queries.base.builder import QueryBuilderBase
from src.external.pdap.impl.sync.shared.models.mapping import DSSyncIDMapping


class DSAppSyncAgenciesAddInsertLinksQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        mappings: list[DSSyncIDMapping]
    ):
        super().__init__()
        self._mappings = mappings

    async def run(self, session: AsyncSession) -> None:
        raise NotImplementedError