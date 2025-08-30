from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.extract import extract_urls_from_agencies_sync_response
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.links.build import \
    build_links_from_url_mappings_and_sync_responses
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.links.requester import UpdateAgencyURLLinksRequester
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.meta_urls.lookup.extract import \
    extract_agency_ids_from_agencies_sync_response
from src.db.dtos.url.mapping import URLMapping
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
        # Get all existing links
        requester = UpdateAgencyURLLinksRequester(session)

        # Build new links from sync responses and URL mappings
        sync_urls: list[str] = extract_urls_from_agencies_sync_response(self._sync_responses)
        url_mappings: list[URLMapping] = await requester.get_url_mappings(urls=sync_urls)
        new_links: list[LinkURLAgencyPydantic] = build_links_from_url_mappings_and_sync_responses(
            url_mappings=url_mappings,
            sync_responses=self._sync_responses,
        )

        sync_agency_ids: list[int] = extract_agency_ids_from_agencies_sync_response(self._sync_responses)
        old_links: list[LinkURLAgencyPydantic] = await requester.get_current_agency_url_links(
            agency_ids=sync_agency_ids,
        )

        new_set: set[LinkURLAgencyPydantic] = set(new_links)
        old_set: set[LinkURLAgencyPydantic] = set(old_links)

        links_to_add: list[LinkURLAgencyPydantic] = list(new_set - old_set)
        links_to_remove: list[LinkURLAgencyPydantic] = list(old_set - new_set)

        await requester.add_agency_url_links(links=links_to_add)
        await requester.remove_agency_url_links(links=links_to_remove)

