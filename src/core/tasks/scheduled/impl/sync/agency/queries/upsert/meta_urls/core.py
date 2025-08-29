from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.meta_urls.lookup.response import MetaURLLookupResponse
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.meta_urls.mapper import AgencyIDMetaURLMapper
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.meta_urls.requester import UpdateMetaURLsRequester
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.meta_urls.response import AgencyURLMappings
from src.db.dtos.url.mapping import URLMapping
from src.db.queries.base.builder import QueryBuilderBase
from src.external.pdap.dtos.sync.agencies import AgenciesSyncResponseInnerInfo
from src.util.url_mapper import URLMapper


class UpsertMetaUrlsQueryBuilder(QueryBuilderBase):
    """Add and update meta URLs for agencies."""

    def __init__(self, sync_responses: list[AgenciesSyncResponseInnerInfo]):
        super().__init__()
        self.sync_responses = sync_responses

    async def run(self, session: AsyncSession) -> list[AgencyURLMappings]:

        requester = UpdateMetaURLsRequester(session)

        lookup_responses: list[MetaURLLookupResponse] = \
            await requester.lookup_meta_urls(self.sync_responses)
        new_url_mappings = \
            await requester.add_new_urls_to_database(lookup_responses)
        existing_url_mappings = \
            await requester.update_existing_urls(lookup_responses)

        all_url_mappings: list[URLMapping] = existing_url_mappings + new_url_mappings

        return self._build_responses(all_url_mappings)


    def _build_responses(self, all_url_mappings: list[URLMapping]) -> list[AgencyURLMappings]:
        agency_id_mapper = AgencyIDMetaURLMapper(self.sync_responses)
        url_mapper = URLMapper(all_url_mappings)

        responses: list[AgencyURLMappings] = []
        for agency_id in agency_id_mapper.get_all_ids():
            url_ids: list[int] = []
            agency_urls: list[str] = agency_id_mapper.get_urls(agency_id)
            for agency_url in agency_urls:
                url_ids.append(url_mapper.get_id(agency_url))
            response = AgencyURLMappings(
                agency_id=agency_id,
                url_ids=url_ids,
            )
            responses.append(response)

        return responses



