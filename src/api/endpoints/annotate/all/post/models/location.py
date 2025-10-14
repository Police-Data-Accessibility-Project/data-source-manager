from pydantic import BaseModel, model_validator


class AnnotationPostLocationInfo(BaseModel):
    not_found: bool = False
    location_ids: list[int] = []

    @property
    def empty(self) -> bool:
        return len(self.location_ids) == 0

    @model_validator(mode="after")
    def forbid_not_found_if_location_ids(self):
        if self.not_found and len(self.location_ids) > 0:
            raise ValueError("not_found must be False if location_ids is not empty")
        return self