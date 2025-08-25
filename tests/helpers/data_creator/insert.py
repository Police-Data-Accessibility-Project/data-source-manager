from src.db.client.async_ import AsyncDatabaseClient
from src.db.templates.markers.bulk.insert import BulkInsertableModel


async def bulk_insert_all(
    adb_client: AsyncDatabaseClient,
    lists_of_models: list[list[BulkInsertableModel]],
):
    for list_of_models in lists_of_models:
        await adb_client.bulk_insert(list_of_models)