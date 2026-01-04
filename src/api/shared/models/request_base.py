from pydantic import BaseModel, ConfigDict


class RequestBase(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True
    )