from pydantic import BaseModel


class LocationIDSubtaskRunInfo(BaseModel):
    error: str | None = None
    linked_url_ids: list[int] | None = None

    @property
    def is_success(self) -> bool:
        return self.error is None

    @property
    def has_linked_urls(self) -> bool:
        return len(self.linked_url_ids) > 0