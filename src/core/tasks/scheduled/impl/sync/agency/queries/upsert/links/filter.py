from src.core.tasks.scheduled.impl.sync.agency.queries.upsert.links.models.mappings import AgencyURLMappings


def filter_non_relevant_mappings(
    mappings: list[AgencyURLMappings],
    relevant_agency_ids: list[int]
) -> list[AgencyURLMappings]:
    relevant_mappings: list[AgencyURLMappings] = []
    for mapping in mappings:
        if mapping.agency_id in relevant_agency_ids:
            relevant_mappings.append(mapping)
    return relevant_mappings