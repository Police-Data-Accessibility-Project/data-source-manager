from pydantic import BaseModel, Field, model_validator

from src.external.pdap.impl.sync.meta_urls._shared.content import MetaURLSyncContentModel


class AddMetaURLsInnerRequest(BaseModel):
    request_id: int
    content: MetaURLSyncContentModel


class AddMetaURLsOuterRequest(BaseModel):
    meta_urls: list[AddMetaURLsInnerRequest] = Field(max_length=1000)

    @model_validator(mode="after")
    def all_request_ids_unique(self):
        if len(self.meta_urls) != len(
            set([meta_url.request_id for meta_url in self.meta_urls])
        ):
            raise ValueError("All request_ids must be unique")
        return self
