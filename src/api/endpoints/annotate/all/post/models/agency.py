from pydantic import BaseModel, model_validator


class AnnotationPostAgencyInfo(BaseModel):
    not_found: bool = False
    agency_ids: list[int] = []

    @property
    def empty(self) -> bool:
        return len(self.agency_ids) == 0

    @model_validator(mode="after")
    def forbid_not_found_if_agency_ids(self):
        if self.not_found and len(self.agency_ids) > 0:
            raise ValueError("not_found must be False if agency_ids is not empty")
        return self
