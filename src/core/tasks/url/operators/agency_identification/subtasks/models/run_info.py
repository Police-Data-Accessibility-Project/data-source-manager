from pydantic import BaseModel


class AgencyIDSubtaskRunInfo(BaseModel):
    error: str | None = None
    linked_url_ids: list[int] | None = None

    @property
    def is_success(self) -> bool:
        return self.error is None