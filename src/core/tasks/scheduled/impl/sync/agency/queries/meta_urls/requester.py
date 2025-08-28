from src.core.tasks.scheduled.impl.sync.agency.queries.meta_urls.convert import \
    extract_agency_ids_from_agencies_sync_response
from src.core.tasks.scheduled.impl.sync.agency.queries.meta_urls.lookup.core import LookupAgencyMetaURLsQueryBuilder
from src.core.tasks.scheduled.impl.sync.agency.queries.meta_urls.lookup.response import AgencyMetaURLLookupResponse
from src.db.templates.requester import RequesterBase
from src.external.pdap.dtos.sync.agencies import AgenciesSyncResponseInnerInfo


class UpdateMetaURLsRequester(RequesterBase):

    async def lookup_meta_urls(self, agencies: list[AgenciesSyncResponseInnerInfo]) -> list[AgencyMetaURLLookupResponse]:
        agency_ids: list[int] = extract_agency_ids_from_agencies_sync_response(agencies)
        return await self.run_query_builder(
            LookupAgencyMetaURLsQueryBuilder(
                agency_ids
            )
        )

    async def add_meta_urls(self) -> None:
        raise NotImplementedError

    async def update_meta_urls(self) -> None:
        raise NotImplementedError

    async def add_agency_url_links(self) -> None:
        raise NotImplementedError

    async def remove_agency_url_links(self) -> None:
        raise NotImplementedError