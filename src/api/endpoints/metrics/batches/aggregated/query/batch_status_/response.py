from pydantic import BaseModel

from src.collectors.enums import CollectorType
from src.core.enums import BatchStatus


class BatchStatusCountByBatchStrategyResponseDTO(BaseModel):
    strategy: CollectorType
    status: BatchStatus
    count: int