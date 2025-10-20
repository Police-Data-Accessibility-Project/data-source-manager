from pydantic import BaseModel

from src.db.models.impl.agency.enums import AgencyType, JurisdictionType


class AgencyPutRequest(BaseModel):
    name: str | None = None
    type: AgencyType | None = None
    jurisdiction_type: JurisdictionType | None = None
