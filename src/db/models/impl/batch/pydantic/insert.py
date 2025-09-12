from datetime import datetime

from src.core.enums import BatchStatus
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.templates.markers.bulk.insert import BulkInsertableModel


class BatchInsertModel(BulkInsertableModel):
    strategy: str
    status: BatchStatus
    parameters: dict
    user_id: int
    date_generated: datetime

    @classmethod
    def sa_model(cls) -> type[Batch]:
        return Batch