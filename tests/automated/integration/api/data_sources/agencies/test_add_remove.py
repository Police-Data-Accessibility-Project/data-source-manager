from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from tests.helpers.api_test_helper import APITestHelper


async def test_agencies_add_remove(
    api_test_helper: APITestHelper,
    test_url_data_source_id: int,
    test_agency_id: int
):
    api_test_helper.request_validator.post_v3(
        url=f"/data-sources/{test_url_data_source_id}/agencies/{test_agency_id}",
    )
    adb_client: AsyncDatabaseClient = api_test_helper.adb_client()

    links: list[LinkURLAgency] = await adb_client.get_all(LinkURLAgency)
    assert len(links) == 1
    assert links[0].agency_id == test_agency_id
    assert links[0].url_id == test_url_data_source_id

    api_test_helper.request_validator.delete_v3(
        url=f"/data-sources/{test_url_data_source_id}/agencies/{test_agency_id}",
    )

    links: list[LinkURLAgency] = await adb_client.get_all(LinkURLAgency)
    assert len(links) == 0