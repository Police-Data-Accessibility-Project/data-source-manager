from collections import defaultdict

from src.external.pdap.dtos.sync.agencies import AgenciesSyncResponseInnerInfo


class AgencyIDMetaURLMapper:

    def __init__(self, sync_responses: list[AgenciesSyncResponseInnerInfo]):
        self._meta_url_to_agency_id: dict[str, list[int]] = defaultdict(list)
        self._agency_id_to_meta_urls: dict[int, list[str]] = defaultdict(list)
        for sync_response in sync_responses:
            for meta_url in sync_response.meta_urls:
                self._meta_url_to_agency_id[meta_url].append(sync_response.agency_id)
                self._agency_id_to_meta_urls[sync_response.agency_id].append(meta_url)


    def get_ids(self, url: str) -> list[int]:
        return self._meta_url_to_agency_id[url]

    def get_urls(self, id: int) -> list[str]:
        return self._agency_id_to_meta_urls[id]