import datetime

from src.db.templates.markers.bulk.insert import BulkInsertableModel


class URLErrorInfoPydantic(BulkInsertableModel):
    task_id: int
    url_id: int
    error: str
    updated_at: datetime.datetime = None
