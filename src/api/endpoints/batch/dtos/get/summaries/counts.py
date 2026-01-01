from pydantic import BaseModel


class BatchSummaryURLCounts(BaseModel):
    total: int
    pending: int
    not_relevant: int
    submitted: int
    errored: int
