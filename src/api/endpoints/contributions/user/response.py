from pydantic import BaseModel, Field

class ContributionsUserAgreement(BaseModel):
    record_type: float = Field(ge=0, le=1)
    agency: float = Field(ge=0, le=1)
    url_type: float = Field(ge=0, le=1)

class ContributionsUserResponse(BaseModel):
    count_validated: int
    agreement: ContributionsUserAgreement