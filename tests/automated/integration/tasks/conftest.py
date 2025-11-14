from unittest.mock import MagicMock, AsyncMock

import pytest
from pdap_access_manager.access_manager.async_ import AccessManagerAsync

from src.external.pdap.client import PDAPClient


@pytest.fixture
def mock_pdap_client() -> PDAPClient:
    mock_access_manager = AsyncMock(
        spec=AccessManagerAsync
    )
    mock_access_manager.data_sources_url = "http://example.com"
    mock_access_manager.build_url = MagicMock(
        return_value="http://example.com"
    )
    mock_access_manager.jwt_header = AsyncMock(
        return_value={"Authorization": "Bearer token"}
    )
    pdap_client = PDAPClient(
        access_manager=mock_access_manager
    )
    return pdap_client
