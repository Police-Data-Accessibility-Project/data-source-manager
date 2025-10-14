from typing import Optional

from pydantic import BaseModel

from src.collectors.impl.muckrock.enums import AgencyLookupResponseType


class AgencyLookupResponse(BaseModel):
    name: str | None
    type: AgencyLookupResponseType
    error: str | None = None
