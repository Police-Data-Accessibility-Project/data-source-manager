import pytest

from src.core.tasks.scheduled.impl.huggingface.operator import PushToHuggingFaceTaskOperator
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.url.html.compressed.sqlalchemy import URLCompressedHTML


@pytest.mark.asyncio
async def test_huggingface_task_duplicate_html_content_not_picked_up(
    adb_client_test: AsyncDatabaseClient,
    operator: PushToHuggingFaceTaskOperator,
    test_url_data_source_id: int,
    test_url_data_source_id_2: int
):

    # Add HTML content with the same hash
    uch_1 = URLCompressedHTML(
        url_id=test_url_data_source_id,
        compressed_html=b"test"
    )
    uch_2 = URLCompressedHTML(
        url_id=test_url_data_source_id_2,
        compressed_html=b"test"
    )
    await adb_client_test.add_all([
        uch_1,
        uch_2
    ])

    # Confirm task meets prerequisites
    assert await operator.meets_task_prerequisites()

    # Refresh materialized view
    await adb_client_test.refresh_materialized_views()

    # Confirm task does not meet prerequisites
    assert not await operator.meets_task_prerequisites()

