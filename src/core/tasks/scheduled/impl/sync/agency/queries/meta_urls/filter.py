from src.core.tasks.scheduled.impl.sync.agency.queries.meta_urls.extract import \
    extract_url_mappings_from_agency_meta_url_lookup_response
from src.core.tasks.scheduled.impl.sync.agency.queries.meta_urls.lookup.response import AgencyMetaURLLookupResponse
from src.core.tasks.scheduled.impl.sync.agency.queries.meta_urls.mapper import AgencyIDMetaURLMapper
from src.core.tasks.scheduled.impl.sync.agency.queries.meta_urls.models.new_url_agencies import NewURLAgenciesMapping
from src.core.tasks.scheduled.impl.sync.agency.queries.meta_urls.models.subset import UpdateMetaAgenciesSubset
from src.db.dtos.url.mapping import URLMapping
from src.db.models.impl.link.url_agency.pydantic import LinkURLAgencyPydantic
from src.external.pdap.dtos.sync.agencies import AgenciesSyncResponseInnerInfo
from src.util.url_mapper import URLMapper


def filter_add_and_remove_meta_urls(
    lookup_responses: list[AgencyMetaURLLookupResponse],
    sync_responses: list[AgenciesSyncResponseInnerInfo]
) -> UpdateMetaAgenciesSubset:

    url_mappings: list[URLMapping] = extract_url_mappings_from_agency_meta_url_lookup_response(
        lookup_responses
    )
    url_mapper = URLMapper(list(url_mappings))

    agency_meta_url_mapper = AgencyIDMetaURLMapper(
        sync_responses
    )

    urls_to_add: list[NewURLAgenciesMapping] = []
    links_to_add: list[LinkURLAgencyPydantic] = []
    links_to_remove: list[LinkURLAgencyPydantic] = []

    for lookup_response in lookup_responses:
        if not lookup_response.exists_in_db:
            # All meta_urls in sync must be added
            urls_in_sync: list[str] = agency_meta_url_mapper.get_urls(
                lookup_response.agency_id
            )

            for url in urls_in_sync:
                urls_to_add.append(
                    NewURLAgenciesMapping(
                        agency_id=lookup_response.agency_id,
                        url=url
                    )
                )

        # If it already exists in the database, compare the meta_urls and see if they differ
        urls_in_db: list[str] = lookup_response.meta_urls

        urls_in_sync: list[str] = agency_meta_url_mapper.get_urls(
            lookup_response.agency_id
        )

        in_db_not_sync: list[str] = list(set(urls_in_db) - set(urls_in_sync))
        in_sync_not_db: list[str] = list(set(urls_in_sync) - set(urls_in_db))

        # For meta_urls in sync but not db, add to urls_to_add

        # For meta_urls in db but not sync, add to links_to_remove

        if lookup_response.exists_in_db:
            lookup_response.url_mappings = url_mapper.get_url_mappings(
                lookup_response.agency_id
            )
        else:
            lookup_response.url_mappings = url_mapper.get_url_mappings(
                lookup_response.agency_id
            )

