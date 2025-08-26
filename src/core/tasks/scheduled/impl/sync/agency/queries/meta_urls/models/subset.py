from pydantic import BaseModel

from src.core.tasks.scheduled.impl.sync.agency.queries.meta_urls.models.new_url_agencies import NewURLAgenciesMapping
from src.db.models.impl.link.url_agency.pydantic import LinkURLAgencyPydantic


class UpdateMetaAgenciesSubset(BaseModel):
    urls_to_add: list[NewURLAgenciesMapping]
    links_to_add: list[LinkURLAgencyPydantic]
    links_to_remove: list[LinkURLAgencyPydantic]