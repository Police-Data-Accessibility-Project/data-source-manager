from src.core.tasks.scheduled.impl.sync.agency.queries.meta_urls.update.params import UpdateMetaURLsParams
from src.external.pdap.dtos.sync.agencies import AgenciesSyncResponseInnerInfo


def extract_agency_ids_from_agencies_sync_response(
    responses: list[AgenciesSyncResponseInnerInfo]
) -> list[int]:
    agency_ids: list[int] = []
    for response in responses:
        agency_ids.append(response.id)
    return agency_ids


def convert_to_update_meta_urls_params(agencies: list[AgenciesSyncResponseInnerInfo]) -> list[UpdateMetaURLsParams]:
    raise NotImplementedError