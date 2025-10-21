from http import HTTPStatus

from fastapi import HTTPException

from src.api.endpoints.suggest.url.models.request import URLSuggestionRequest
from src.api.endpoints.suggest.url.models.response.model import URLSuggestResponse
from src.api.endpoints.suggest.url.queries.core import URLSuggestQueryBuilder
from src.db.client.async_ import AsyncDatabaseClient
from src.util.url import is_valid_url


async def suggest_url_wrapper(
    request: URLSuggestionRequest,
    adb_client: AsyncDatabaseClient,
) -> URLSuggestResponse:
    if not is_valid_url(request.url):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid URL"
        )

    return await adb_client.run_query_builder(
        URLSuggestQueryBuilder(request)
    )