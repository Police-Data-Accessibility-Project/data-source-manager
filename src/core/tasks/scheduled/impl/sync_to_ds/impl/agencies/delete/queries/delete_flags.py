from sqlalchemy.ext.asyncio import AsyncSession

from src.db.queries.base.builder import QueryBuilderBase


class DSAppSyncAgenciesDeleteRemoveFlagsQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        ds_agency_ids: list[int]
    ):
        super().__init__()
        self._ds_agency_ids = ds_agency_ids

    async def run(self, session: AsyncSession) -> None:
        raise NotImplementedError