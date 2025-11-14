from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from tests.helpers.api_test_helper import APITestHelper


async def test_agencies_add_remove(
    api_test_helper: APITestHelper,
    test_url_data_source_id: int,
    test_agency_id_2: int,
    test_agency_id: int
):
    api_test_helper.request_validator.post_v3(
        url=f"/data-sources/{test_url_data_source_id}/agencies/{test_agency_id_2}",
    )
    adb_client: AsyncDatabaseClient = api_test_helper.adb_client()

    links: list[LinkURLAgency] = await adb_client.get_all(LinkURLAgency)
    assert len(links) == 2
    assert {link.agency_id for link in links} == {test_agency_id_2, test_agency_id}
    assert {link.url_id for link in links} == {test_url_data_source_id}

    api_test_helper.request_validator.delete_v3(
        url=f"/data-sources/{test_url_data_source_id}/agencies/{test_agency_id_2}",
    )

    links: list[LinkURLAgency] = await adb_client.get_all(LinkURLAgency)
    assert len(links) == 1