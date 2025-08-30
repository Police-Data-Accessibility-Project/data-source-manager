from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.lookup.response import MetaURLLookupResponse
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.meta_urls.filter import filter_urls_in_sync
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.meta_urls.requester import UpdateMetaURLsRequester
from src.db.queries.base.builder import QueryBuilderBase
from src.external.pdap.dtos.sync.agencies import AgenciesSyncResponseInnerInfo


class UpsertMetaUrlsQueryBuilder(QueryBuilderBase):
    """Add and update meta URLs for agencies."""

    def __init__(self, sync_responses: list[AgenciesSyncResponseInnerInfo]):
        super().__init__()
        self.sync_responses = sync_responses

    async def run(self, session: AsyncSession) -> None:

        requester = UpdateMetaURLsRequester(session)

        lookup_responses: list[MetaURLLookupResponse] = \
            await requester.lookup_meta_urls(self.sync_responses)
        await requester.add_new_urls_to_database(lookup_responses)
        filtered_lookup_responses: list[MetaURLLookupResponse] = \
            filter_urls_in_sync(self.sync_responses, lookup_responses=lookup_responses)
        await requester.update_existing_urls(filtered_lookup_responses)



