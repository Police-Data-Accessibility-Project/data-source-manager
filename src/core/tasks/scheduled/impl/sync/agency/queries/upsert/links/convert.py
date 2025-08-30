from collections import defaultdict

from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.links.models.mappings import AgencyURLMappings
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.lookup.response import MetaURLLookupResponse
from src.db.dtos.url.mapping import URLMapping
from src.db.models.impl.link.url_agency.pydantic import LinkURLAgencyPydantic
from src.external.pdap.dtos.sync.agencies import AgenciesSyncResponseInnerInfo
from src.util.url_mapper import URLMapper


def _convert_lookup_response_to_url_mapping(
    response: MetaURLLookupResponse
) -> URLMapping:
    return URLMapping(
        url_id=response.url_id,
        url=response.url,
    )

def convert_sync_and_lookup_responses_to_sync_mappings(
    sync_responses: list[AgenciesSyncResponseInnerInfo],
    lookup_responses: list[MetaURLLookupResponse]
) -> list[AgencyURLMappings]:
    """Get all prior Agency-URL mappings.
    Leveraging the lookup responses to get the URL ids
    """

    # Get the URL ids for the URLs
    lookup_url_mappings: list[URLMapping] = [
        _convert_lookup_response_to_url_mapping(response)
        for response in lookup_responses
    ]
    url_mapper = URLMapper(lookup_url_mappings)

    # Associate Agency with URLs in Sync Responses
    agency_to_sync_urls: dict[int, list[str]] = {}
    for response in sync_responses:
        agency_to_sync_urls[response.agency_id] = response.meta_urls

    # Create Agency-URL Mappings
    agency_url_mappings: list[AgencyURLMappings] = []
    for agency in agency_to_sync_urls:
        url_ids: list[int] = []
        for url in agency_to_sync_urls[agency]:
            url_id: int = url_mapper.get_id(url)
            url_ids.append(url_id)
        agency_url_mapping = AgencyURLMappings(
            agency_id=agency,
            url_ids=url_ids,
        )
        agency_url_mappings.append(agency_url_mapping)

    return agency_url_mappings


def convert_lookup_responses_to_mappings(
    responses: list[MetaURLLookupResponse]
) -> list[AgencyURLMappings]:
    """Get all current Agency-URL mappings."""
    agency_to_url_ids: dict[int, list[int]] = defaultdict(list)
    for response in responses:
        for agency_id in response.agency_ids:
            agency_to_url_ids[agency_id].append(response.url_id)

    agency_url_mappings: list[AgencyURLMappings] = []
    for agency_id in agency_to_url_ids:
        agency_url_mappings.append(AgencyURLMappings(
            agency_id=agency_id,
            url_ids=agency_to_url_ids[agency_id],
        ))

    return agency_url_mappings

def convert_mappings_to_links(
    mappings: list[AgencyURLMappings]
) -> set[LinkURLAgencyPydantic]:
    links: set[LinkURLAgencyPydantic] = set()
    for mapping in mappings:
        for url_id in mapping.url_ids:
            links.add(LinkURLAgencyPydantic(url_id=url_id, agency_id=mapping.agency_id))

    return links