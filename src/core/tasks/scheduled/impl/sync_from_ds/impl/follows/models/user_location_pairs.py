"""

Design Notes:
    - I contemplated having this be a simple tuple, but reasoned it'd be more future-proof
    if I used a Pydantic Model, so it would fail loudly in cause the API response
    structure changes.

"""

from pydantic import BaseModel

from src.core.tasks.scheduled.impl.sync_from_ds.impl.follows.types import LocationID, UserID

class UserLocationPairs(BaseModel):
    user_id: UserID
    location_id: LocationID

    class Config:
        frozen = True