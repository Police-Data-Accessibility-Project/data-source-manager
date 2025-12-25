from pydantic import BaseModel


class SyncFollowGetInnerResponse(BaseModel):
    user_id: int
    location_id: int

class SyncFollowGetOuterResponse(BaseModel):
    follows: list[SyncFollowGetInnerResponse]
