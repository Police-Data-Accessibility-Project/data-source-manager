from pydantic import BaseModel

from src.db.dtos.url.mapping_.simple import SimpleURLMapping


class InsertURLsInfo(BaseModel):
    url_mappings: list[SimpleURLMapping]
    url_ids: list[int]
    total_count: int = 0
    original_count: int = 0
    duplicate_count: int = 0
