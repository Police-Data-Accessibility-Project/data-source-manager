from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync.agency.queries.meta_urls.convert import \
    extract_agency_ids_from_agencies_sync_response
from src.core.tasks.scheduled.impl.sync.agency.queries.meta_urls.lookup.response import AgencyMetaURLLookupResponse
from src.core.tasks.scheduled.impl.sync.agency.queries.meta_urls.lookup.url.response import MetaURLLookupResponse
from src.core.tasks.scheduled.impl.sync.agency.queries.meta_urls.requester import UpdateMetaURLsRequester
from src.db.dtos.url.mapping import URLMapping
from src.db.queries.base.builder import QueryBuilderBase
from src.external.pdap.dtos.sync.agencies import AgenciesSyncResponseInnerInfo


class UpdateMetaUrlsQueryBuilder(QueryBuilderBase):
    """Updates meta URLs for agencies."""

    def __init__(self, agencies: list[AgenciesSyncResponseInnerInfo]):
        super().__init__()
        self.responses = agencies

    async def run(self, session: AsyncSession) -> None:

        requester = UpdateMetaURLsRequester(session)

        # Get URLs to Add
        lookup_responses: list[MetaURLLookupResponse] = await requester.lookup_meta_urls(self.responses)

        urls_to_add: list[str] = filter_urls_to_add(lookup_responses)

        # Add new URLs to database
        new_url_mappings: list[URLMapping] = await requester.add_meta_urls(urls_to_add)
        existing_url_mappings: list[URLMapping] = filter_existing_url_mappings(lookup_responses)

        all_url_mappings: list[URLMapping] = existing_url_mappings + new_url_mappings





        # Update existing URLs




        # Update existing URLs as validated meta URLs

        # Update Agency-URL links

        # Get existing meta URLs
        lookup_responses: list[AgencyMetaURLLookupResponse] = \
            await requester.lookup_meta_urls(self.responses)

        # Compare with new meta URLs, separate into add, remove, and do nothing

        # Add new meta URLs

        # Remove old meta URLs

