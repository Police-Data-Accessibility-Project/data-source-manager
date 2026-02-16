import datetime

from pydantic import BaseModel

from src.db.models.impl.url.core.enums import URLSource


class URLInfo(BaseModel):
    id: int | None = None
    batch_id: int | None= None
    url: str
    collector_metadata: dict | None = None
    updated_at: datetime.datetime | None = None
    created_at: datetime.datetime | None = None
    name: str | None = None
    source: URLSource | None = None
