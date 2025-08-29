from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.meta_urls.lookup.response import MetaURLLookupResponse


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
    return [
        lookup_response
        for lookup_response in lookup_responses
        if lookup_response.exists_in_db
    ]