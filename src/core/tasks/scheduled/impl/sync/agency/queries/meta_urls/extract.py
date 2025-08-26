from src.core.tasks.scheduled.impl.sync.agency.queries.meta_urls.lookup.response import AgencyMetaURLLookupResponse
from src.db.dtos.url.mapping import URLMapping


def extract_url_mappings_from_agency_meta_url_lookup_response(
    lookup_responses: list[AgencyMetaURLLookupResponse]
) -> list[URLMapping]:
    url_mappings: set[URLMapping] = set()
    for lookup_response in lookup_responses:
        for url_mapping in lookup_response.url_mappings:
            url_mappings.add(url_mapping)
    return list(url_mappings)