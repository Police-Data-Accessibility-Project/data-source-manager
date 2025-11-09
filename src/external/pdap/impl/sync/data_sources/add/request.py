from pydantic import BaseModel, Field, model_validator

from src.external.pdap.impl.sync.data_sources._shared.content import DataSourceSyncContentModel


class AddDataSourcesInnerRequest(BaseModel):
    request_id: int
    content: DataSourceSyncContentModel


class AddDataSourcesOuterRequest(BaseModel):
    data_sources: list[AddDataSourcesInnerRequest] = Field(max_length=1000)

    @model_validator(mode="after")
    def all_request_ids_unique(self):
        if len(self.data_sources) != len(
            set([data_source.request_id for data_source in self.data_sources])
        ):
            raise ValueError("All request_ids must be unique")
        return self
