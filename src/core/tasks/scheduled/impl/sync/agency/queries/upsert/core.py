from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.links.core import UpdateAgencyURLLinksQueryBuilder
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.meta_urls.core import UpsertMetaUrlsQueryBuilder
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.meta_urls.response import AgencyURLMappings
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.convert import \
    convert_agencies_sync_response_to_agencies_upsert
from src.db.models.impl.agency.pydantic.upsert import AgencyUpsertModel
from src.db.queries.base.builder import QueryBuilderBase
from src.external.pdap.dtos.sync.agencies import AgenciesSyncResponseInnerInfo

from src.db.helpers.session import session_helper as sh

class UpsertAgenciesQueryBuilder(QueryBuilderBase):

    def __init__(self, sync_responses: list[AgenciesSyncResponseInnerInfo]):
        super().__init__()
        self.sync_responses = sync_responses

    async def run(self, session: AsyncSession) -> None:
        # Upsert Agencies
        agency_upserts: list[AgencyUpsertModel] = convert_agencies_sync_response_to_agencies_upsert(self.sync_responses)
        await sh.bulk_upsert(session=session, models=agency_upserts)

        # Add and update Meta URLs
        meta_urls_query_builder = UpsertMetaUrlsQueryBuilder(self.sync_responses)
        upsert_meta_urls_responses: list[AgencyURLMappings] = await meta_urls_query_builder.run(session=session)

        # Add and remove URL-Agency Links
        update_url_links_query_builder = UpdateAgencyURLLinksQueryBuilder(upsert_meta_urls_responses)
        await update_url_links_query_builder.run(session=session)
