from pydantic import BaseModel

from src.db.client.async_ import AsyncDatabaseClient
from tests.helpers.api_test_helper import APITestHelper


class ReadOnlyTestHelper(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    adb_client: AsyncDatabaseClient
    api_test_helper: APITestHelper

    agency_1_id: int
    agency_1_location_id: int
    agency_2_id: int
    agency_2_location_id: int

    minimal_data_source: int
    maximal_data_source: int
    url_meta_url_id: int
