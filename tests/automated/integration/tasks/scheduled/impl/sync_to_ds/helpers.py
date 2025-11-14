from http import HTTPStatus
from typing import Any
from unittest.mock import AsyncMock

from pdap_access_manager import RequestInfo, RequestType, ResponseInfo
from pydantic import BaseModel

from src.external.pdap.client import PDAPClient
from tests.helpers.mock import get_last_call_arguments


def get_last_request(
    mock_pdap_client: PDAPClient
) -> RequestInfo:
    return get_last_call_arguments(mock_pdap_client.access_manager.make_request)[0]

def extract_and_validate_sync_request(
    mock_pdap_client: PDAPClient,
    expected_path: str,
    expected_model: type[BaseModel]
) -> Any:
    assert mock_pdap_client.access_manager.make_request.call_count == 1
    request_info: RequestInfo = get_last_request(mock_pdap_client)
    assert request_info.type_ == RequestType.POST
    full_expected_url: str = f"http://example.com/v3/source-manager/{expected_path}"
    assert request_info.url == full_expected_url, f"Expected URL: {full_expected_url}, Actual URL: {request_info.url}"
    return expected_model(**request_info.json_)

def mock_make_request(
    mock_pdap_client: PDAPClient,
    data: BaseModel
) -> None:
    mock_pdap_client.access_manager.make_request = AsyncMock(
        return_value=ResponseInfo(
            status_code=HTTPStatus.OK,
            data=data.model_dump(mode='json')
        )
    )