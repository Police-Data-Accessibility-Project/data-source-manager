class URLRequestIDMapper:

    def __init__(self):
        self._request_id_to_url_id_mapper: dict[int, int] = {}

    def add_mapping(self, request_id: int, url_id: int) -> None:
        self._request_id_to_url_id_mapper[request_id] = url_id

    def get_url_id_by_request_id(self, request_id: int) -> int:
        return self._request_id_to_url_id_mapper[request_id]
