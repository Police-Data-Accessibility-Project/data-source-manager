from src.api.endpoints.meta_url.by_id.agencies.shared.check import check_is_meta_url
from src.api.shared.agency.delete.query import RemoveURLAgencyLinkQueryBuilder
from src.db.client.async_ import AsyncDatabaseClient


async def delete_meta_url_agency_link(
    url_id: int,
    agency_id: int,
    adb_client: AsyncDatabaseClient
) -> None:
    await check_is_meta_url(url_id=url_id, adb_client=adb_client)
    await adb_client.run_query_builder(
        RemoveURLAgencyLinkQueryBuilder(
            url_id=url_id,
            agency_id=agency_id
        )
    )