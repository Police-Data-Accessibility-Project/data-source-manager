import types

import pytest

from src.core.tasks.url.operators.html.core import URLHTMLTaskOperator
from src.core.tasks.url.operators.html.scraper.parser.core import HTMLResponseParser
from src.db.client.async_ import AsyncDatabaseClient
from src.external.url_request.dtos.url_response import URLResponseInfo
from tests.automated.integration.tasks.url.impl.html.mocks.methods import mock_parse


class _MockURLRequestInterface:

    async def make_requests_with_html(self, urls: list[str]) -> list[URLResponseInfo]:
        return []

@pytest.fixture
def operator(
    adb_client_test: AsyncDatabaseClient
) -> URLHTMLTaskOperator:
    html_parser = HTMLResponseParser()
    html_parser.parse = types.MethodType(mock_parse, html_parser)
    operator = URLHTMLTaskOperator(
        adb_client=adb_client_test,
        url_request_interface=_MockURLRequestInterface(),
        html_parser=html_parser
    )
    return operator