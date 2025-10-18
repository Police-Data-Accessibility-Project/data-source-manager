from src.db.dtos.url.mapping_.full import FullURLMapping
from src.util.models.full_url import FullURL


class FullURLMapper:

    def __init__(self, mappings: list[FullURLMapping]):
        self._url_to_id = {
            mapping.full_url.id_form: mapping.url_id
            for mapping in mappings
        }
        self._id_to_url = {
            mapping.url_id: mapping.full_url
            for mapping in mappings
        }

    def get_id(self, full_url: FullURL) -> int:
        return self._url_to_id[full_url.id_form]

    def get_ids(self, full_urls: list[FullURL]) -> list[int]:
        return [
            self._url_to_id[full_url.id_form]
            for full_url in full_urls
        ]

    def get_all_ids(self) -> list[int]:
        return list(self._url_to_id.values())

    def get_all_urls(self) -> list[FullURL]:
        return list(self._id_to_url.values())

    def get_url(self, url_id: int) -> FullURL:
        return self._id_to_url[url_id]

    def get_mappings_by_url(self, full_urls: list[FullURL]) -> list[FullURLMapping]:
        return [
            FullURLMapping(
                url_id=self._url_to_id[full_url.id_form],
                full_url=full_url
            ) for full_url in full_urls
        ]

    def add_mapping(self, mapping: FullURLMapping) -> None:
        self._url_to_id[mapping.full_url.id_form] = mapping.url_id
        self._id_to_url[mapping.url_id] = mapping.full_url

    def add_mappings(self, mappings: list[FullURLMapping]) -> None:
        for mapping in mappings:
            self.add_mapping(mapping)