from uuid import UUID

from src.api.endpoints.annotate.all.post.models.request import AllAnnotationPostInfo
from src.api.endpoints.annotate.anonymous.get.response import GetNextURLForAnonymousAnnotationResponse
from src.util.helper_functions import update_if_not_none
from tests.automated.integration.api._helpers.RequestValidator import RequestValidator


async def get_next_url_for_anonymous_annotation(
    request_validator: RequestValidator,
    session_id: UUID | None = None,
    offset: int | None = None,
) -> GetNextURLForAnonymousAnnotationResponse:
    url = "/annotate/anonymous"
    params = {}
    update_if_not_none(
        target=params,
        source={
            "session_id": session_id,
            "offset": offset
        }
    )

    data = request_validator.get(
        url=url,
        params=params
    )
    return GetNextURLForAnonymousAnnotationResponse(**data)

async def post_and_get_next_url_for_anonymous_annotation(
    request_validator: RequestValidator,
    url_id: int,
    all_annotation_post_info: AllAnnotationPostInfo,
    session_id: UUID,
    get_next_url: bool = True
) -> GetNextURLForAnonymousAnnotationResponse:
    url = f"/annotate/anonymous/{url_id}"
    params = {}
    update_if_not_none(
        target=params,
        source={
            "session_id": session_id,
            "get_next_url": get_next_url
        }
    )
    data = request_validator.post(
        url=url,
        json=all_annotation_post_info.model_dump(mode='json'),
        params=params
    )
    return GetNextURLForAnonymousAnnotationResponse(**data)