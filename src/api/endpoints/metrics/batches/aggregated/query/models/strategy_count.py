from pydantic import BaseModel

from src.collectors.enums import CollectorType


class CountByBatchStrategyResponse(BaseModel):
    strategy: CollectorType
    count: int