from src.core.tasks.url.operators.agency_identification.subtasks.impl.nlp_location_match_.processor.models.mappings.url_id_search_params import \
    URLToSearchParamsMapping
from src.external.pdap.dtos.search_agency_by_location.params import SearchAgencyByLocationParams


def _extract_all_search_params(
    url_to_search_params_mappings: list[URLToSearchParamsMapping]
) -> list[SearchAgencyByLocationParams]:
    all_search_params: list[SearchAgencyByLocationParams] = []
    for mapping in url_to_search_params_mappings:
        all_search_params.extend(mapping.search_params)
    return all_search_params
