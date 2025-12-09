from uuid import UUID

from pydantic import BaseModel

from src.api.endpoints.annotate.all.get.models.response import GetNextURLForAllAnnotationInnerResponse


class GetNextURLForAnonymousAnnotationResponse(BaseModel):
    next_annotation: GetNextURLForAllAnnotationInnerResponse | None
    session_id: UUID