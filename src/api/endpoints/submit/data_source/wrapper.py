from fastapi import HTTPException

from src.api.endpoints.submit.data_source.query import SubmitDataSourceURLProposalQueryBuilder
from src.api.endpoints.submit.data_source.request import DataSourceSubmissionRequest
from src.api.endpoints.submit.data_source.response import SubmitDataSourceURLProposalResponse
from src.db.client.async_ import AsyncDatabaseClient
from src.db.queries.urls_exist.model import URLExistsResult
from src.db.queries.urls_exist.query import URLsExistInDBQueryBuilder
from src.util.models.full_url import FullURL
from src.util.url import is_valid_url


async def submit_data_source_url_proposal(
    request: DataSourceSubmissionRequest,
    adb_client: AsyncDatabaseClient
) -> SubmitDataSourceURLProposalResponse:

    if not is_valid_url(request.source_url):
        raise HTTPException(
            status_code=400,
            detail="Invalid URL"
        )

    url_exists_results: URLExistsResult = (await adb_client.run_query_builder(
        URLsExistInDBQueryBuilder(
            full_urls=[FullURL(request.source_url)]
        )
    ))[0]
    if url_exists_results.exists:
        raise HTTPException(
            status_code=400,
            detail="URL already exists in database."
        )

    return await adb_client.run_query_builder(
        SubmitDataSourceURLProposalQueryBuilder(
            request=request
        )
    )