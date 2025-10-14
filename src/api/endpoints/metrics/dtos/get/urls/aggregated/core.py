import datetime

from pydantic import BaseModel

from src.core.enums import RecordType
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.views.url_status.enums import URLStatusViewEnum

class GetMetricsURLValidatedOldestPendingURL(BaseModel):
    url_id: int
    created_at: datetime.datetime

class GetMetricsURLsAggregatedResponseDTO(BaseModel):
    count_urls_total: int
    count_urls_status: dict[URLStatusViewEnum, int]
    count_urls_type: dict[URLType, int]
    count_urls_record_type: dict[RecordType, int]
    oldest_pending_url: GetMetricsURLValidatedOldestPendingURL | None
