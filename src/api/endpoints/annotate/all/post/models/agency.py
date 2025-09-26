from pydantic import BaseModel

from src.db.models.impl.agency.enums import JurisdictionType, AgencyType


class AnnotationNewAgencySuggestionInfo(BaseModel):
    name: str
    location_id: int
    jurisdiction_type: JurisdictionType | None
    agency_type: AgencyType | None

class AnnotationPostAgencyInfo(BaseModel):
    new_agency_suggestion: AnnotationNewAgencySuggestionInfo | None = None
    agency_ids: list[int] = []

    @property
    def empty(self) -> bool:
        return self.new_agency_suggestion is None and len(self.agency_ids) == 0
