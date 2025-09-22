from contextlib import contextmanager
from datetime import datetime, timedelta
from unittest.mock import patch, create_autospec, AsyncMock

from src.collectors.enums import URLStatus
from src.core.enums import RecordType
from src.db.client.async_ import AsyncDatabaseClient
from src.db.models.impl.flag.url_validated.enums import URLType
from src.external.pdap.client import PDAPClient
from src.external.pdap.dtos.sync.data_sources import DataSourcesSyncResponseInfo, DataSourcesSyncResponseInnerInfo
from src.external.pdap.enums import ApprovalStatus, DataSourcesURLStatus
from tests.automated.integration.tasks.scheduled.impl.sync.data_sources.setup.queries.url_.url import \
    TestDataSourcesSyncURLSetupQueryBuilder
from tests.helpers.simple_test_data_functions import generate_test_url


@contextmanager
def patch_sync_data_sources(side_effects: list):
    with patch.object(
        PDAPClient,
        "sync_data_sources",
        side_effect=side_effects
    ):
        yield



def set_up_mock_pdap_client_responses(
    mock_pdap_client: PDAPClient,
    responses: list[DataSourcesSyncResponseInfo | Exception]
) -> None:
    """
    Modifies:
    - pdap_client.sync_data_sources
    """
    mock_sync_data_sources = AsyncMock(
        side_effect=responses + [DataSourcesSyncResponseInfo(data_sources=[])]
    )
    mock_pdap_client.sync_data_sources = mock_sync_data_sources

async def set_up_urls(
    adb_client: AsyncDatabaseClient,
    record_type: RecordType,
    validated_type: URLType | None = None,
    previously_synced: bool = False,
) -> list[int]:
    """Creates 2 test URLs."""

    builder = TestDataSourcesSyncURLSetupQueryBuilder(
        record_type=record_type,
        validated_type=validated_type,
        previously_synced=previously_synced,
    )

    return await adb_client.run_query_builder(builder)

def _generate_test_data_source_name(i: int) -> str:
    return f"Test Data Source {i}"

def _generate_test_data_source_description(i: int) -> str:
    return f"Test Data Source Description {i}"

def set_up_sync_response_info(
    ids: list[int],
    record_type: RecordType,
    agency_ids: list[int],
    approval_status: ApprovalStatus,
    ds_url_status: DataSourcesURLStatus,
) -> DataSourcesSyncResponseInfo:
    yesterday = datetime.now() - timedelta(days=1)
    inner_info_list: list[DataSourcesSyncResponseInnerInfo] = []
    for id_ in ids:
        inner_info_list.append(
            DataSourcesSyncResponseInnerInfo(
                id=id_,
                url=generate_test_url(id_),
                name=_generate_test_data_source_name(id_),
                description=_generate_test_data_source_description(id_),
                record_type=record_type,
                agency_ids=agency_ids,
                approval_status=approval_status,
                url_status=ds_url_status,
                updated_at=yesterday,
            )
        )
    return DataSourcesSyncResponseInfo(
        data_sources=inner_info_list,
    )