from src.core.tasks.url.operators.probe.queries.insert_redirects.models.url_response_map import URLResponseMapping
from src.db.dtos.url.mapping_.full import FullURLMapping
from src.external.url_request.probe.models.response import URLProbeResponse
from src.util.models.full_url import FullURL


def map_url_mappings_to_probe_responses(
    url_mappings: list[FullURLMapping],
    url_to_probe_responses: dict[FullURL, URLProbeResponse]
) -> list[URLResponseMapping]:
    results = []
    for url_mapping in url_mappings:
        response = url_to_probe_responses[url_mapping.full_url]
        results.append(
            URLResponseMapping(
                url_mapping=url_mapping,
                response=response
            )
        )
    return results