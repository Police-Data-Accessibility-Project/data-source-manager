from pydantic import Field, BaseModel

from src.external.pdap.impl.sync.meta_urls._shared.content import MetaURLSyncContentModel


class UpdateMetaURLsInnerRequest(BaseModel):
    app_id: int
    content: MetaURLSyncContentModel


class UpdateMetaURLsOuterRequest(BaseModel):
    meta_urls: list[UpdateMetaURLsInnerRequest] = Field(max_length=1000)
