from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.agency.ds_link.sqlalchemy import DSAppLinkAgency
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.flag.ds_delete.agency import FlagDSDeleteAgency
from src.db.queries.base.builder import QueryBuilderBase


class DeleteAgencyQueryBuilder(QueryBuilderBase):

    def __init__(
            self,
            agency_id: int,
    ):
        super().__init__()
        self.agency_id = agency_id

    async def run(self, session: AsyncSession) -> None:
        # Check for existence of DS App Link. If so, add deletion flag
        query = (
            select(
                DSAppLinkAgency
            )
            .where(
                DSAppLinkAgency.agency_id == self.agency_id
            )
        )
        ds_app_link_agency: DSAppLinkAgency | None = await self.sh.one_or_none(session, query=query)
        if ds_app_link_agency is not None:
            flag = FlagDSDeleteAgency(
                ds_agency_id=ds_app_link_agency.ds_agency_id,
            )
            session.add(flag)

        # Delete Agency
        statement = (
            delete(Agency)
            .where(Agency.id == self.agency_id)
        )
        await session.execute(statement)