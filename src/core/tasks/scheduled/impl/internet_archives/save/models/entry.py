from pydantic import BaseModel

from src.db.dtos.url.mapping_.simple import SimpleURLMapping


class InternetArchivesSaveTaskEntry(BaseModel):
    url: str
    url_id: int
    is_new: bool

    def to_url_mapping(self) -> SimpleURLMapping:
        return SimpleURLMapping(
            url_id=self.url_id,
            url=self.url
        )