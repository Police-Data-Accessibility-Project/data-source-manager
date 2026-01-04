from pydantic import BaseModel

from src.db.client.async_ import AsyncDatabaseClient
from tests.helpers.api_test_helper import APITestHelper


class ReadOnlyTestHelper(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    # Clients
    adb_client: AsyncDatabaseClient
    api_test_helper: APITestHelper

    # Agencies
    agency_1_id: int
    agency_1_location_id: int
    agency_2_id: int
    agency_2_location_id: int

    # URLs
    minimal_data_source_url_id: int
    maximal_data_source_url_id: int
    url_meta_url_id: int
    unvalidated_url_id: int

    # Users
    user_1_id: int
    user_2_id: int


