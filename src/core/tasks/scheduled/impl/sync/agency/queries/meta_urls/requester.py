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