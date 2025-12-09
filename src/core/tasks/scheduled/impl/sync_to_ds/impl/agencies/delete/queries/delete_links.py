from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.agency.ds_link.sqlalchemy import DSAppLinkAgency
from src.db.queries.base.builder import QueryBuilderBase


class DSAppSyncAgenciesDeleteRemoveLinksQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        ds_agency_ids: list[int]
    ):
        super().__init__()
        self._ds_agency_ids = ds_agency_ids

    async def run(self, session: AsyncSession) -> None:
        statement = (
            delete(DSAppLinkAgency)
            .where(DSAppLinkAgency.ds_agency_id.in_(self._ds_agency_ids))
        )
        await session.execute(statement)