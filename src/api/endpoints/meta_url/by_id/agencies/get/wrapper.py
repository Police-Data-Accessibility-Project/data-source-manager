from src.api.endpoints.agencies.root.get.response import AgencyGetOuterResponse
from src.api.endpoints.meta_url.by_id.agencies.shared.check import check_is_meta_url
from src.api.shared.agency.get.query import GetRelatedAgenciesQueryBuilder
from src.db.client.async_ import AsyncDatabaseClient


async def get_meta_url_agencies_wrapper(
    url_id: int,
    adb_client: AsyncDatabaseClient
) -> AgencyGetOuterResponse:
    await check_is_meta_url(url_id=url_id, adb_client=adb_client)
    return await adb_client.run_query_builder(
        GetRelatedAgenciesQueryBuilder(url_id=url_id)
    )