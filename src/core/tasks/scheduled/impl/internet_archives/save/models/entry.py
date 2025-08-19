from pydantic import BaseModel

from src.db.dtos.url.mapping import URLMapping


class InternetArchivesSaveTaskEntry(BaseModel):
    url: str
    url_id: int
    is_new: bool

    def to_url_mapping(self) -> URLMapping:
        return URLMapping(
            url_id=self.url_id,
            url=self.url
        )