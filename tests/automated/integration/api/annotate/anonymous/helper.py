from src.api.endpoints.annotate.all.get.models.response import GetNextURLForAllAnnotationResponse
from src.api.endpoints.annotate.all.post.models.request import AllAnnotationPostInfo
from tests.automated.integration.api._helpers.RequestValidator import RequestValidator


async def get_next_url_for_anonymous_annotation(
    request_validator: RequestValidator,
):
    data = request_validator.get(
        url=f"/annotate/anonymous"
    )
    return GetNextURLForAllAnnotationResponse(**data)

async def post_and_get_next_url_for_anonymous_annotation(
    request_validator: RequestValidator,
    url_id: int,
    all_annotation_post_info: AllAnnotationPostInfo,
):
    data = request_validator.post(
        url=f"/annotate/anonymous/{url_id}",
        json=all_annotation_post_info.model_dump(mode='json')
    )
    return GetNextURLForAllAnnotationResponse(**data)