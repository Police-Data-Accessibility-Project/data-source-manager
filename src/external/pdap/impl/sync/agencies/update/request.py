from pydantic import BaseModel, Field

from src.external.pdap.impl.sync.agencies._shared.models.content import AgencySyncContentModel


class UpdateAgenciesInnerRequest(BaseModel):
    app_id: int
    content: AgencySyncContentModel


class UpdateAgenciesOuterRequest(BaseModel):
    agencies: list[UpdateAgenciesInnerRequest] = Field(max_length=1000)
