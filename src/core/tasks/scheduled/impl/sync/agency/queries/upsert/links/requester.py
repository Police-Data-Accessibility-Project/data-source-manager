from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.links.lookup.core import LookupMetaURLAgencyLinksQueryBuilder
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.meta_urls.response import AgencyURLMappings
from src.db.models.impl.link.url_agency.pydantic import LinkURLAgencyPydantic
from src.db.templates.requester import RequesterBase

from src.db.helpers.session import session_helper as sh

class UpdateAgencyURLLinksRequester(RequesterBase):

    async def lookup_meta_url_agency_links(self, agency_ids: list[int]) -> list[AgencyURLMappings]:
        return await LookupMetaURLAgencyLinksQueryBuilder(
            agency_ids=agency_ids
        ).run(session=self.session)

    async def add_agency_url_links(self, links: list[LinkURLAgencyPydantic]) -> None:
        await sh.bulk_insert(self.session, models=links)

    async def remove_agency_url_links(self, links: list[LinkURLAgencyPydantic]) -> None:
        await sh.bulk_delete(self.session, models=links)
