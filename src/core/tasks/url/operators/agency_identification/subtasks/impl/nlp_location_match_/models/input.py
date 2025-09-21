from pydantic import BaseModel

class LocationAnnotation(BaseModel):
    location_id: int
    confidence: int

class LocationAnnotationToAgencyIDMapping(BaseModel):
    location_annotation: LocationAnnotation
    agency_ids: list[int]

class NLPLocationMatchSubtaskInput(BaseModel):
    url_id: int
    mappings: list[LocationAnnotationToAgencyIDMapping]

    @property
    def has_locations_with_agencies(self) -> bool:
        return len(self.mappings) > 0