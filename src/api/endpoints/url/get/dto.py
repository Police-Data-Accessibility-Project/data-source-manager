import datetime

from pydantic import BaseModel

from src.db.enums import URLMetadataAttributeType, ValidationStatus, ValidationSource, TaskType
from src.db.models.materialized_views.url_status.enums import URLStatusViewEnum


class GetURLsResponseErrorInfo(BaseModel):
    task: TaskType
    error: str
    updated_at: datetime.datetime

class GetURLsResponseMetadataInfo(BaseModel):
    id: int
    attribute: URLMetadataAttributeType
    value: str
    validation_status: ValidationStatus
    validation_source: ValidationSource
    created_at: datetime.datetime
    updated_at: datetime.datetime

class GetURLsResponseInnerInfo(BaseModel):
    id: int
    batch_id: int | None
    url: str
    status: URLStatusViewEnum | None
    collector_metadata: dict | None
    updated_at: datetime.datetime
    created_at: datetime.datetime
    errors: list[GetURLsResponseErrorInfo]

class GetURLsResponseInfo(BaseModel):
    urls: list[GetURLsResponseInnerInfo]
    count: int
