from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.flag.ds_delete.agency import FlagDSDeleteAgency
from src.db.queries.base.builder import QueryBuilderBase


class DSAppSyncAgenciesDeleteRemoveFlagsQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        ds_agency_ids: list[int]
    ):
        super().__init__()
        self._ds_agency_ids = ds_agency_ids

    async def run(self, session: AsyncSession) -> None:
        statement = (
            delete(FlagDSDeleteAgency)
            .where(FlagDSDeleteAgency.ds_agency_id.in_(self._ds_agency_ids))
        )
        await session.execute(statement)