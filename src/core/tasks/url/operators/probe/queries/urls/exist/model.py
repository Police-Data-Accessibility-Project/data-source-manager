from pydantic import BaseModel

from src.util.models.full_url import FullURL


class URLExistsResult(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    query_url: FullURL
    db_url: FullURL | None
    url_id: int | None

    @property
    def exists(self) -> bool:
        return self.url_id is not None

    @property
    def urls_match(self) -> bool:
        return self.query_url.id_form == self.db_url.id_form