from src.db.helpers.session import session_helper as sh
from src.db.models.impl.link.url_agency.pydantic import LinkURLAgencyPydantic
from src.db.templates.requester import RequesterBase


class UpdateAgencyURLLinksRequester(RequesterBase):

    async def add_agency_url_links(self, links: list[LinkURLAgencyPydantic]) -> None:
        await sh.bulk_insert(self.session, models=links)

    async def remove_agency_url_links(self, links: list[LinkURLAgencyPydantic]) -> None:
        await sh.bulk_delete(self.session, models=links)
