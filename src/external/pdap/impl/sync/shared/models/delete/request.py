from pydantic import BaseModel


class DSAppSyncDeleteRequestModel(BaseModel):
    ids: list[int]