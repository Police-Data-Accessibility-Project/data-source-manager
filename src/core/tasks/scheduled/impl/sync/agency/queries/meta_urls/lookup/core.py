from sqlalchemy.ext.asyncio import AsyncSession

from src.collectors.impl.muckrock.api_interface.lookup_response import AgencyLookupResponse
from src.core.tasks.scheduled.impl.sync.agency.queries.meta_urls.lookup.response import AgencyMetaURLLookupResponse
from src.db.queries.base.builder import QueryBuilderBase


class LookupAgencyMetaURLsQueryBuilder(QueryBuilderBase):
    """Look up agencies in database, noting those that exist and providing associated meta urls."""

    def __init__(self, agency_ids: list[int]):
        super().__init__()
        self.agency_ids = agency_ids

    async def run(self, session: AsyncSession) -> list[AgencyMetaURLLookupResponse]:
        raise NotImplementedError