import pytest
from fastapi import HTTPException

from tests.helpers.api_test_helper import APITestHelper


def check_forbidden_url_type(
    route: str,
    method: str,
    api_test_helper: APITestHelper,
    **kwargs
) -> None:
    with pytest.raises(HTTPException) as e:
        api_test_helper.request_validator.open_v3(
            url=route,
            method=method,
            **kwargs
        )
    assert e.value.status_code == 400, f"Expected status code 400, got {e.value.status_code}"
    assert e.value.detail['detail'] == 'URL type does not match expected URL type'