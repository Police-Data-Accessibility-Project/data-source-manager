from pydantic import BaseModel, Field


class SuggestionModel(BaseModel):
    id: int
    display_name: str
    user_count: int
    robo_confidence: int | None = Field(
        description="The robo labeler's given confidence for its suggestion. Null if no robo-label occurred.",
        ge=0,
        le=100,
    )

    @property
    def score(self) -> float:
        robo_score = (self.robo_confidence or 0) / 100
        return self.user_count + robo_score