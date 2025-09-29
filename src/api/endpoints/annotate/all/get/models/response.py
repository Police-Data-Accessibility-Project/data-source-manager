from typing import Optional

from pydantic import Field, BaseModel

from src.api.endpoints.annotate.agency.get.dto import GetNextURLForAgencyAgencyInfo
from src.api.endpoints.annotate.all.get.models.agency import AgencyAnnotationResponseOuterInfo
from src.api.endpoints.annotate.all.get.models.location import LocationAnnotationResponseOuterInfo
from src.api.endpoints.annotate.all.get.models.name import NameAnnotationSuggestion
from src.api.endpoints.annotate.all.get.models.record_type import RecordTypeAnnotationSuggestion
from src.api.endpoints.annotate.all.get.models.url_type import URLTypeAnnotationSuggestion
from src.api.endpoints.annotate.dtos.shared.base.response import AnnotationInnerResponseInfoBase
from src.api.endpoints.annotate.relevance.get.dto import RelevanceAnnotationResponseInfo
from src.core.enums import RecordType


class GetNextURLForAllAnnotationInnerResponse(AnnotationInnerResponseInfoBase):
    agency_suggestions: AgencyAnnotationResponseOuterInfo | None = Field(
        title="The auto-labeler's suggestions for agencies"
    )
    location_suggestions: LocationAnnotationResponseOuterInfo | None = Field(
        title="User and Auto-Suggestions for locations"
    )
    url_type_suggestions: list[URLTypeAnnotationSuggestion] = Field(
        title="Whether the auto-labeler identified the URL as relevant or not"
    )
    record_type_suggestions: list[RecordTypeAnnotationSuggestion] = Field(
        title="What record type, if any, user and the auto-labeler identified the URL as"
    )
    name_suggestions: list[NameAnnotationSuggestion] | None = Field(
        title="User and Auto-Suggestions for names"
    )


class GetNextURLForAllAnnotationResponse(BaseModel):
    next_annotation: GetNextURLForAllAnnotationInnerResponse | None