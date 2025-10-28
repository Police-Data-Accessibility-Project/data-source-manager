from pydantic import BaseModel


class LinkUserFollow(BaseModel):
    user_id: int
    location_id: int


class GetFollowsResponse(BaseModel):
    follows: list[LinkUserFollow]

