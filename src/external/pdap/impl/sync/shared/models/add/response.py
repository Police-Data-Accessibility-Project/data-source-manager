from pydantic import BaseModel

class DSAppSyncAddResponseInnerModel(BaseModel):
    request_id: int
    app_id: int

class DSAppSyncAddResponseModel(BaseModel):
    entities: list[DSAppSyncAddResponseInnerModel]