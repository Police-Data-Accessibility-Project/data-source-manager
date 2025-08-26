from src.external.pdap.dtos.sync.agencies import AgenciesSyncResponseInnerInfo


def extract_agency_ids_from_agencies_sync_response(
    responses: list[AgenciesSyncResponseInnerInfo]
) -> list[int]:
    agency_ids: list[int] = []
    for response in responses:
        agency_ids.append(response.id)
    return agency_ids