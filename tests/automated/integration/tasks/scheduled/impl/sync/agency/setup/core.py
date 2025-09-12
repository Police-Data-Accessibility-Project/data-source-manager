from contextlib import contextmanager
from datetime import timedelta, datetime
from unittest.mock import patch, AsyncMock

from src.core.enums import RecordType
from src.db.models.impl.flag.url_validated.enums import URLValidatedType
from src.external.pdap.client import PDAPClient
from src.external.pdap.dtos.sync.agencies import AgenciesSyncResponseInfo, AgenciesSyncResponseInnerInfo
from tests.helpers.data_creator.core import DBDataCreator
from tests.helpers.simple_test_data_functions import generate_test_name


def set_up_mock_pdap_client_responses(
    mock_pdap_client: PDAPClient,
    responses: list[AgenciesSyncResponseInfo | Exception]
) -> None:
    """
    Modifies:
    - pdap_client.sync_agencies
    """
    mock_sync_agencies = AsyncMock(
        side_effect=responses + [AgenciesSyncResponseInfo(agencies=[])]
    )
    mock_pdap_client.sync_agencies = mock_sync_agencies

async def set_up_urls(
    db_data_creator: DBDataCreator,
    record_type: RecordType,
    validated_type: URLValidatedType | None = None,
    agency_ids: list[int] | None = None,
) -> list[int]:
    """Create 2 Test URLs in database."""
    url_ids: list[int] = await db_data_creator.create_urls(record_type=record_type, count=2)
    if validated_type is not None:
        await db_data_creator.create_validated_flags(url_ids=url_ids, validation_type=validated_type)
    if agency_ids is not None:
        await db_data_creator.create_url_agency_links(url_ids=url_ids, agency_ids=agency_ids)
    return url_ids

def set_up_sync_response_info(
    agency_id: int,
    meta_urls: list[str],
) -> AgenciesSyncResponseInfo:
    yesterday = datetime.now() - timedelta(days=1)
    return AgenciesSyncResponseInfo(agencies=[AgenciesSyncResponseInnerInfo(
        agency_id=agency_id,
        meta_urls=meta_urls,
        updated_at=yesterday,
        state_name=None,
        county_name=None,
        locality_name=None,
        display_name=generate_test_name(agency_id)
    )])
