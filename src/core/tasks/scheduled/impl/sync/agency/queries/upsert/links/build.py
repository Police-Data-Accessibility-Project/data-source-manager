from src.db.dtos.url.mapping import URLMapping
from src.db.models.impl.link.url_agency.pydantic import LinkURLAgencyPydantic
from src.external.pdap.dtos.sync.agencies import AgenciesSyncResponseInnerInfo
from src.util.url_mapper import URLMapper

def build_links_from_url_mappings_and_sync_responses(
    url_mappings: list[URLMapping],
    sync_responses: list[AgenciesSyncResponseInnerInfo],
) -> list[LinkURLAgencyPydantic]:

    links: list[LinkURLAgencyPydantic] = []

    mapper = URLMapper(url_mappings)
    for sync_response in sync_responses:
        agency_id: int = sync_response.agency_id
        for meta_url in sync_response.meta_urls:
            url_id: int = mapper.get_id(meta_url)
            link = LinkURLAgencyPydantic(
                agency_id=agency_id,
                url_id=url_id
            )
            links.append(link)
    return links