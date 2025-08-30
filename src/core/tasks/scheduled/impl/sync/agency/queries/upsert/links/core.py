from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.links.convert import \
    convert_lookup_responses_to_mappings, convert_mappings_to_links, convert_sync_and_lookup_responses_to_sync_mappings
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.links.filter import filter_non_relevant_mappings
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.links.requester import UpdateAgencyURLLinksRequester
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.lookup.core import LookupMetaURLsQueryBuilder
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.lookup.extract import \
    extract_agency_ids_from_agencies_sync_response
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.lookup.response import MetaURLLookupResponse
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.links.models.mappings import AgencyURLMappings
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.meta_urls.filter import filter_urls_in_sync
from src.db.models.impl.link.url_agency.pydantic import LinkURLAgencyPydantic
from src.db.queries.base.builder import QueryBuilderBase
from src.external.pdap.dtos.sync.agencies import AgenciesSyncResponseInnerInfo


class UpdateAgencyURLLinksQueryBuilder(QueryBuilderBase):
    """Updates agency URL links."""

    def __init__(
        self,
        sync_responses: list[AgenciesSyncResponseInnerInfo]
    ):
        super().__init__()
        self._sync_responses = sync_responses

    async def run(self, session: AsyncSession) -> None:
        # TODO: Replace with LookupMetaURLLinksQueryBuilder
        # TODO: Include a Lookup for the URL Mappings of the sync URLs

        lookup_responses: list[MetaURLLookupResponse] = \
            await LookupMetaURLsQueryBuilder(self._sync_responses).run(session=session)
        filtered_lookup_responses: list[MetaURLLookupResponse] = \
            filter_urls_in_sync(self._sync_responses, lookup_responses=lookup_responses)

        new_mappings: list[AgencyURLMappings] = convert_sync_and_lookup_responses_to_sync_mappings(
            self._sync_responses,
            lookup_responses=filtered_lookup_responses,
        )
        old_mappings: list[AgencyURLMappings] = self._get_old_mappings(filtered_lookup_responses)

        new_links: set[LinkURLAgencyPydantic] = convert_mappings_to_links(new_mappings)
        old_links: set[LinkURLAgencyPydantic] = convert_mappings_to_links(old_mappings)

        links_to_add: list[LinkURLAgencyPydantic] = list(new_links - old_links)
        links_to_remove: list[LinkURLAgencyPydantic] = list(old_links - new_links)

        requester = UpdateAgencyURLLinksRequester(session)
        await requester.add_agency_url_links(links=links_to_add)
        await requester.remove_agency_url_links(links=links_to_remove)

    def _get_old_mappings(
        self,
        lookup_responses: list[MetaURLLookupResponse]
    ) -> list[AgencyURLMappings]:
        old_mappings: list[AgencyURLMappings] = convert_lookup_responses_to_mappings(lookup_responses)
        relevant_agency_ids: list[int] = extract_agency_ids_from_agencies_sync_response(self._sync_responses)
        # Exclude old mappings that are not relevant
        filtered_old_mappings: list[AgencyURLMappings] = filter_non_relevant_mappings(
            mappings=old_mappings,
            relevant_agency_ids=relevant_agency_ids,
        )
        return filtered_old_mappings



