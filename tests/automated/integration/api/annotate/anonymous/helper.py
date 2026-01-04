from uuid import UUID

from src.api.endpoints.annotate.all.post.models.request import AllAnnotationPostInfo
from src.api.endpoints.annotate.anonymous.get.response import GetNextURLForAnonymousAnnotationResponse
from tests.automated.integration.api._helpers.RequestValidator import RequestValidator


async def get_next_url_for_anonymous_annotation(
    request_validator: RequestValidator,
    session_id: UUID | None = None
) -> GetNextURLForAnonymousAnnotationResponse:
    url = "/annotate/anonymous"
    if session_id is not None:
        url += f"?session_id={session_id}"

    data = request_validator.get(
        url=url
    )
    return GetNextURLForAnonymousAnnotationResponse(**data)

async def post_and_get_next_url_for_anonymous_annotation(
    request_validator: RequestValidator,
    url_id: int,
    all_annotation_post_info: AllAnnotationPostInfo,
    session_id: UUID
) -> GetNextURLForAnonymousAnnotationResponse:
    url = f"/annotate/anonymous/{url_id}?session_id={session_id}"
    data = request_validator.post(
        url=url,
        json=all_annotation_post_info.model_dump(mode='json')
    )
    return GetNextURLForAnonymousAnnotationResponse(**data)