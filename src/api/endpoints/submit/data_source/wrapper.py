from fastapi import HTTPException

from src.api.endpoints.submit.data_source.models.response.standard import SubmitDataSourceURLProposalResponse
from src.api.endpoints.submit.data_source.queries.core import SubmitDataSourceURLProposalQueryBuilder

from src.api.endpoints.submit.data_source.queries.duplicate import GetDataSourceDuplicateQueryBuilder
from src.api.endpoints.submit.data_source.request import DataSourceSubmissionRequest
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

    full_url = FullURL(request.source_url)

    url_exists_results: URLExistsResult = (await adb_client.run_query_builder(
        URLsExistInDBQueryBuilder(
            full_urls=[full_url]
        )
    ))[0]
    if url_exists_results.exists:
        await adb_client.run_query_builder(
            GetDataSourceDuplicateQueryBuilder(
                url=full_url.id_form
            )
        )

    return await adb_client.run_query_builder(
        SubmitDataSourceURLProposalQueryBuilder(
            request=request
        )
    )