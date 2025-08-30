from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.links.lookup_.links import LookupMetaURLLinksQueryBuilder
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.links.lookup_.url import LookupURLQueryBuilder
from src.db.dtos.url.mapping import URLMapping
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.link.url_agency.pydantic import LinkURLAgencyPydantic
from src.db.templates.requester import RequesterBase


class UpdateAgencyURLLinksRequester(RequesterBase):

    async def get_url_mappings(self, urls: list[str]) -> list[URLMapping]:
        return await LookupURLQueryBuilder(urls=urls).run(session=self.session)

    async def get_current_agency_url_links(self, agency_ids: list[int]) -> list[LinkURLAgencyPydantic]:
        return await LookupMetaURLLinksQueryBuilder(agency_ids=agency_ids).run(session=self.session)

    async def add_agency_url_links(self, links: list[LinkURLAgencyPydantic]) -> None:
        await sh.bulk_insert(self.session, models=links)

    async def remove_agency_url_links(self, links: list[LinkURLAgencyPydantic]) -> None:
        await sh.bulk_delete(self.session, models=links)
