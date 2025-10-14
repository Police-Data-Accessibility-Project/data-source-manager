from pydantic import BaseModel


class ContributionsLeaderboardInnerResponse(BaseModel):
    user_id: int
    count: int

class ContributionsLeaderboardResponse(BaseModel):
    leaderboard: list[ContributionsLeaderboardInnerResponse]