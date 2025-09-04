from pydantic import BaseModel, ConfigDict


class USState(BaseModel):
    model_config = ConfigDict(frozen=True)

    name: str
    iso: str
