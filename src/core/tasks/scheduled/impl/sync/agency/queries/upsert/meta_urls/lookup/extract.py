from src.external.pdap.dtos.sync.agencies import AgenciesSyncResponseInnerInfo


def extract_agency_ids_from_agencies_sync_response(
    responses: list[AgenciesSyncResponseInnerInfo]
) -> list[int]:
    return [
        response.agency_id
        for response in responses
    ]
