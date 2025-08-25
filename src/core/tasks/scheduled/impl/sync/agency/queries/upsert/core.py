from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.convert import \
    convert_agencies_sync_response_to_agencies_upsert
from src.db.models.impl.agency.pydantic.upsert import AgencyUpsertModel
from src.db.queries.base.builder import QueryBuilderBase
from src.external.pdap.dtos.sync.agencies import AgenciesSyncResponseInnerInfo

from src.db.helpers.session import session_helper as sh

class UpsertAgenciesQueryBuilder(QueryBuilderBase):

    def __init__(self, agencies: list[AgenciesSyncResponseInnerInfo]):
        super().__init__()
        self.agencies = agencies

    async def run(self, session: AsyncSession) -> None:
        agency_upserts: list[AgencyUpsertModel] = convert_agencies_sync_response_to_agencies_upsert(self.agencies)
        await sh.bulk_upsert(session=session, models=agency_upserts)
