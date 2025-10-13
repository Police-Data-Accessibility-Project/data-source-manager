from pydantic import BaseModel, model_validator

from src.core.enums import RecordType
from src.core.exceptions import FailedValidationException
from src.db.models.impl.flag.url_validated.enums import URLType


class GetURLsForAutoValidationResponse(BaseModel):
    url_id: int
    location_id: int | None
    agency_id: int | None
    url_type: URLType
    record_type: RecordType | None
    name: str | None

    @model_validator(mode="after")
    def forbid_record_type_if_not_data_source(self):
        if self.url_type == URLType.DATA_SOURCE:
            return self
        if self.record_type is not None:
            raise FailedValidationException("record_type must be None if suggested_status is META_URL")
        return self


    @model_validator(mode="after")
    def require_record_type_if_data_source(self):
        if self.url_type == URLType.DATA_SOURCE and self.record_type is None:
            raise FailedValidationException("record_type must be provided if suggested_status is DATA_SOURCE")
        return self

    @model_validator(mode="after")
    def require_location_if_relevant(self):
        if self.url_type not in [
            URLType.META_URL,
            URLType.DATA_SOURCE,
            URLType.INDIVIDUAL_RECORD,
        ]:
            return self
        if self.location_id is None:
            raise FailedValidationException("location_id must be provided if suggested_status is META_URL or DATA_SOURCE")
        return self


    @model_validator(mode="after")
    def require_agency_id_if_relevant(self):
        if self.url_type not in [
            URLType.META_URL,
            URLType.DATA_SOURCE,
            URLType.INDIVIDUAL_RECORD,
        ]:
            return self
        if self.agency_id is None:
            raise FailedValidationException("agency_id must be provided if suggested_status is META_URL or DATA_SOURCE")
        return self

    @model_validator(mode="after")
    def forbid_all_else_if_not_relevant(self):
        if self.url_type != URLType.NOT_RELEVANT:
            return self
        if self.record_type is not None:
            raise FailedValidationException("record_type must be None if suggested_status is NOT RELEVANT")
        if self.agency_id is not None:
            raise FailedValidationException("agency_ids must be empty if suggested_status is NOT RELEVANT")
        if self.location_id is not None:
            raise FailedValidationException("location_ids must be empty if suggested_status is NOT RELEVANT")
        return self


