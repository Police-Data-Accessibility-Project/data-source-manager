from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.extract import extract_urls_from_agencies_sync_response
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.meta_urls.lookup.response import MetaURLLookupResponse
from src.external.pdap.dtos.sync.agencies import AgenciesSyncResponseInnerInfo


def filter_urls_to_add(
    lookup_responses: list[MetaURLLookupResponse]
) -> list[str]:
    return [
        lookup_response.url
        for lookup_response in lookup_responses
        if not lookup_response.exists_in_db
    ]

def filter_existing_url_mappings(
    lookup_responses: list[MetaURLLookupResponse]
) -> list[MetaURLLookupResponse]:
    """Filter only URL mappings that already exist in the database."""
    return [
        lookup_response
        for lookup_response in lookup_responses
        if lookup_response.exists_in_db
    ]

def filter_urls_in_sync(
    sync_responses: list[AgenciesSyncResponseInnerInfo],
    lookup_responses: list[MetaURLLookupResponse]
) -> list[MetaURLLookupResponse]:
    """Filter only URLs that are in sync responses."""
    sync_urls: set[str] = set(
        extract_urls_from_agencies_sync_response(sync_responses)
    )
    filtered_lookup_responses: list[MetaURLLookupResponse] = []
    for lookup_response in lookup_responses:
        if lookup_response.url in sync_urls:
            filtered_lookup_responses.append(lookup_response)
    return filtered_lookup_responses