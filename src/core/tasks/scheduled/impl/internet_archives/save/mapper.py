from src.core.tasks.scheduled.impl.internet_archives.save.models.entry import InternetArchivesSaveTaskEntry


class URLToEntryMapper:

    def __init__(self, entries: list[InternetArchivesSaveTaskEntry]):
        self._url_to_entry: dict[str, InternetArchivesSaveTaskEntry] = {
            entry.url: entry for entry in entries
        }

    def get_is_new(self, url: str) -> bool:
        return self._url_to_entry[url].is_new

    def get_url_id(self, url: str) -> int:
        return self._url_to_entry[url].url_id

    def get_all_urls(self) -> list[str]:
        return list(self._url_to_entry.keys())
