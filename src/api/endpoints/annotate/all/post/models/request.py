from pydantic import BaseModel, model_validator

from src.api.endpoints.annotate.all.post.models.name import AnnotationPostNameInfo
from src.core.enums import RecordType
from src.core.exceptions import FailedValidationException
from src.db.models.impl.flag.url_validated.enums import URLType


class AllAnnotationPostInfo(BaseModel):
    suggested_status: URLType
    record_type: RecordType | None = None
    agency_ids: list[int]
    location_ids: list[int]
    name_info: AnnotationPostNameInfo = AnnotationPostNameInfo()

    @model_validator(mode="after")
    def forbid_record_type_if_meta_url_or_individual_record(self):
        if self.suggested_status not in [
            URLType.META_URL,
            URLType.INDIVIDUAL_RECORD,
        ]:
            return self
        if self.record_type is not None:
            raise FailedValidationException("record_type must be None if suggested_status is META_URL")
        return self

    @model_validator(mode="after")
    def forbid_all_else_if_not_relevant(self):
        if self.suggested_status != URLType.NOT_RELEVANT:
            return self
        if self.record_type is not None:
            raise FailedValidationException("record_type must be None if suggested_status is NOT RELEVANT")
        if len(self.agency_ids) > 0:
            raise FailedValidationException("agency_ids must be empty if suggested_status is NOT RELEVANT")
        if len(self.location_ids) > 0:
            raise FailedValidationException("location_ids must be empty if suggested_status is NOT RELEVANT")
        return self


    @model_validator(mode="after")
    def deprecate_agency_meta_url_record_type(self):
        if self.record_type is None:
            return self
        if self.record_type == RecordType.CONTACT_INFO_AND_AGENCY_META:
            raise FailedValidationException("Contact Info & Agency Meta Record Type is Deprecated.")
        return self
