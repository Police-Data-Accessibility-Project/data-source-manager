from pydantic import BaseModel, model_validator

from src.core.enums import RecordType
from src.core.exceptions import FailedValidationException
from src.db.models.impl.flag.url_validated.enums import URLType


class AllAnnotationPostInfo(BaseModel):
    suggested_status: URLType
    record_type: RecordType | None = None
    agency_ids: list[int]
    location_ids: list[int]

    @model_validator(mode="after")
    def forbid_record_type_if_meta_url(self):
        if self.suggested_status == URLType.META_URL and self.record_type is not None:
            raise FailedValidationException("record_type must be None if suggested_status is META_URL")
        return self

    @model_validator(mode="after")
    def require_record_type_if_data_source(self):
        if self.suggested_status == URLType.DATA_SOURCE and self.record_type is None:
            raise FailedValidationException("record_type must be provided if suggested_status is DATA_SOURCE")
        return self

    @model_validator(mode="after")
    def require_location_if_meta_url_or_data_source(self):
        if self.suggested_status not in [URLType.META_URL, URLType.DATA_SOURCE]:
            return self
        if len(self.location_ids) == 0:
            raise FailedValidationException("location_ids must be provided if suggested_status is META_URL or DATA_SOURCE")
        return self

    @model_validator(mode="after")
    def require_agency_id_if_meta_url_or_data_source(self):
        if self.suggested_status not in [URLType.META_URL, URLType.DATA_SOURCE]:
            return self
        if len(self.agency_ids) == 0:
            raise FailedValidationException("agencies must be provided if suggested_status is META_URL or DATA_SOURCE")
        return self

    @model_validator(mode="after")
    def forbid_all_else_if_not_meta_url_or_data_source(self):
        if self.suggested_status in [URLType.META_URL, URLType.DATA_SOURCE]:
            return self
        if self.record_type is not None:
            raise FailedValidationException("record_type must be None if suggested_status is not META_URL or DATA_SOURCE")
        if len(self.agency_ids) > 0:
            raise FailedValidationException("agency_ids must be empty if suggested_status is not META_URL or DATA_SOURCe")
        if len(self.location_ids) > 0:
            raise FailedValidationException("location_ids must be empty if suggested_status is not META_URL or DATA_SOURCE")
        return self


    @model_validator(mode="after")
    def deprecate_agency_meta_url_record_type(self):
        if self.record_type is None:
            return self
        if self.record_type == RecordType.CONTACT_INFO_AND_AGENCY_META:
            raise FailedValidationException("Contact Info & Agency Meta Record Type is Deprecated.")
        return self
