from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.links.subsets import AgencyMetaURLLinkSubsets
from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.meta_urls.response import AgencyURLMappings

def _convert_to_agency_id_to_url_ids(mappings: list[AgencyURLMappings]) -> dict[int, list[int]]:
    agency_id_to_url_ids: dict[int, list[int]] = {}
    for mapping in mappings:
        agency_id_to_url_ids[mapping.agency_id] = mapping.url_ids
    return agency_id_to_url_ids


def filter_agency_meta_url_link_subsets(
    new_mappings: list[AgencyURLMappings],
    old_mappings: list[AgencyURLMappings],
) -> list[AgencyMetaURLLinkSubsets]:

    agency_id_to_new_url_ids: dict[int, list[int]] = _convert_to_agency_id_to_url_ids(new_mappings)
    agency_id_to_old_url_ids: dict[int, list[int]] = _convert_to_agency_id_to_url_ids(old_mappings)

    subset_list: list[AgencyMetaURLLinkSubsets] = []

    for agency_id in agency_id_to_new_url_ids.keys():

        new_url_ids: set[int] = set(agency_id_to_new_url_ids[agency_id])
        old_url_ids: set[int] = set(agency_id_to_old_url_ids.get(agency_id, []))

        url_ids_to_add: list[int] = list(new_url_ids - old_url_ids)
        url_ids_to_remove: list[int] = list(old_url_ids - new_url_ids)
        url_ids_to_do_nothing_with: list[int] = list(old_url_ids & new_url_ids)

        subsets = AgencyMetaURLLinkSubsets(
            agency_id=agency_id,
            add=url_ids_to_add,
            remove=url_ids_to_remove,
            do_nothing=url_ids_to_do_nothing_with,
        )
        subset_list.append(subsets)

    return subset_list


