from pydantic import BaseModel, model_validator, Field

from src.external.pdap.impl.sync.agencies._shared.models.content import AgencySyncContentModel


class AddAgenciesInnerRequest(BaseModel):
    request_id: int
    content: AgencySyncContentModel


class AddAgenciesOuterRequest(BaseModel):
    agencies: list[AddAgenciesInnerRequest] = Field(max_length=1000)

    @model_validator(mode="after")
    def all_request_ids_unique(self):
        if len(self.agencies) != len(
            set([agency.request_id for agency in self.agencies])
        ):
            raise ValueError("All request_ids must be unique")
        return self
