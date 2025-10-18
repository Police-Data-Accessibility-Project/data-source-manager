from pydantic import BaseModel

from src.db.dtos.url.mapping_.simple import SimpleURLMapping


class FinalReviewSetupInfo(BaseModel):
    batch_id: int
    url_mapping: SimpleURLMapping
    user_agency_id: int | None
    name_suggestion_id: int | None
