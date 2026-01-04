from typing import Any

from pdap_access_manager.access_manager.async_ import AccessManagerAsync
from pdap_access_manager.enums import RequestType
from pdap_access_manager.models.request import RequestInfo
from pdap_access_manager.models.response import ResponseInfo

from src.external.pdap._templates.request_builder import PDAPRequestBuilderBase
from src.external.pdap.dtos.unique_url_duplicate import UniqueURLDuplicateInfo


class PDAPClient:

    def __init__(
        self,
        access_manager: AccessManagerAsync,
    ):
        self.access_manager = access_manager

    async def run_request_builder(
        self,
        request_builder: PDAPRequestBuilderBase
    ) -> Any:
        return await request_builder.run(self.access_manager)
