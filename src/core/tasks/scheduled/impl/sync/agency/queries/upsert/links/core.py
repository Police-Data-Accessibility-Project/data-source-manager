from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.links.filter import filter_agency_meta_url_link_subsets
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.links.requester import UpdateAgencyURLLinksRequester
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.links.subsets import AgencyMetaURLLinkSubsets
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.meta_urls.response import AgencyURLMappings
from src.db.models.impl.link.url_agency.pydantic import LinkURLAgencyPydantic
from src.db.queries.base.builder import QueryBuilderBase


class UpdateAgencyURLLinksQueryBuilder(QueryBuilderBase):
    """Updates agency URL links."""

    def __init__(
        self,
        responses: list[AgencyURLMappings]
    ):
        super().__init__()
        self._new_mappings = responses

    async def run(self, session: AsyncSession) -> None:

        requester = UpdateAgencyURLLinksRequester(session)
        agency_ids: list[int] = [response.agency_id for response in self._new_mappings]
        old_mappings: list[AgencyURLMappings] = await requester.lookup_meta_url_agency_links(agency_ids)

        subset_list: list[AgencyMetaURLLinkSubsets] = filter_agency_meta_url_link_subsets(
            new_mappings=self._new_mappings,
            old_mappings=old_mappings,
        )

        links_to_add: list[LinkURLAgencyPydantic] = []
        links_to_remove: list[LinkURLAgencyPydantic] = []
        for subsets in subset_list:
            agency_id: int = subsets.agency_id
            for url_id in subsets.add:
                links_to_add.append(
                    LinkURLAgencyPydantic(url_id=url_id, agency_id=agency_id)
                )
            for url_id in subsets.remove:
                links_to_remove.append(
                    LinkURLAgencyPydantic(url_id=url_id, agency_id=agency_id)
                )

        await requester.add_agency_url_links(links=links_to_add)
        await requester.remove_agency_url_links(links=links_to_remove)



