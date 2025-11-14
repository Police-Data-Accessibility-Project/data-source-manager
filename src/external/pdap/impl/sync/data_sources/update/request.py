from pydantic import BaseModel, Field

from src.external.pdap.impl.sync.data_sources._shared.content import DataSourceSyncContentModel


class UpdateDataSourcesInnerRequest(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    app_id: int
    content: DataSourceSyncContentModel


class UpdateDataSourcesOuterRequest(BaseModel):
    data_sources: list[UpdateDataSourcesInnerRequest] = Field(max_length=1000)
