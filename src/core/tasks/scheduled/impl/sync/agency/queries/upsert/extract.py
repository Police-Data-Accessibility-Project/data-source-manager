from src.external.pdap.dtos.sync.agencies import AgenciesSyncResponseInnerInfo


def extract_urls_from_agencies_sync_response(
    responses: list[AgenciesSyncResponseInnerInfo]
) -> list[str]:
    url_set: set[str] = set()
    for response in responses:
        for url in response.meta_urls:
            url_set.add(url)

    return list(url_set)
