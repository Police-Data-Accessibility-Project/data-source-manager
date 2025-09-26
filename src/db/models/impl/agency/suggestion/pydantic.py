from pydantic import BaseModel

from src.db.models.impl.agency.enums import JurisdictionType, AgencyType
from src.db.models.impl.agency.suggestion.sqlalchemy import NewAgencySuggestion
from src.db.models.templates_.base import Base


class NewAgencySuggestionPydantic(BaseModel):

    name: str
    location_id: int
    jurisdiction_type: JurisdictionType | None
    agency_type: AgencyType | None

    @classmethod
    def sa_model(cls) -> type[Base]:
        return NewAgencySuggestion