from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync.agency.queries.meta_urls.convert import \
    extract_agency_ids_from_agencies_sync_response
from src.core.tasks.scheduled.impl.sync.agency.queries.meta_urls.lookup.response import AgencyMetaURLLookupResponse
from src.core.tasks.scheduled.impl.sync.agency.queries.meta_urls.requester import UpdateMetaURLsRequester
from src.db.queries.base.builder import QueryBuilderBase
from src.external.pdap.dtos.sync.agencies import AgenciesSyncResponseInnerInfo


class UpdateMetaUrlsQueryBuilder(QueryBuilderBase):
    """Updates meta URLs for agencies."""

    def __init__(self, agencies: list[AgenciesSyncResponseInnerInfo]):
        super().__init__()
        self.agencies = agencies

    async def run(self, session: AsyncSession) -> None:

        requester = UpdateMetaURLsRequester(session)

        # Add new URLs to database

        # Update existing URLs as validated meta URLs

        # Update Agency-URL links

        # Get existing meta URLs
        lookup_responses: list[AgencyMetaURLLookupResponse] = \
            await requester.lookup_meta_urls(self.agencies)

        # Compare with new meta URLs, separate into add, remove, and do nothing

        # Add new meta URLs

        # Remove old meta URLs

