from src.api.endpoints.data_source.by_id.agency.shared.check import check_is_data_source_url
from src.api.shared.agency.delete.query import RemoveURLAgencyLinkQueryBuilder
from src.db.client.async_ import AsyncDatabaseClient


async def delete_data_source_agency_link(
    url_id: int,
    agency_id: int,
    adb_client: AsyncDatabaseClient
) -> None:
    await check_is_data_source_url(url_id=url_id, adb_client=adb_client)
    await adb_client.run_query_builder(
        RemoveURLAgencyLinkQueryBuilder(
            url_id=url_id,
            agency_id=agency_id
        )
    )