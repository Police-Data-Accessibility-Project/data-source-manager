from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.agency.ds_link.sqlalchemy import DSAppLinkAgency
from src.db.queries.base.builder import QueryBuilderBase
from src.external.pdap.impl.sync.shared.models.add.response import DSAppSyncAddResponseInnerModel


class DSAppSyncAgenciesAddInsertLinksQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        mappings: list[DSAppSyncAddResponseInnerModel]
    ):
        super().__init__()
        self._mappings = mappings

    async def run(self, session: AsyncSession) -> None:
        inserts: list[DSAppLinkAgency] = []
        for mapping in self._mappings:
            inserts.append(
                DSAppLinkAgency(
                    ds_agency_id=mapping.app_id,
                    agency_id=mapping.request_id,
                )
            )
        session.add_all(inserts)