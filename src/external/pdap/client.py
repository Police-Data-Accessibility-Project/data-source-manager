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

    async def is_url_duplicate(
        self,
        url_to_check: str
    ) -> bool:
        """
        Check if a URL is unique. Returns duplicate info otherwise
        """
        url: str = f"{self.access_manager.data_sources_url}/v2/check/unique-url"

        request_info = RequestInfo(
            type_=RequestType.GET,
            url=url,
            params={
                "url": url_to_check
            }
        )
        response_info: ResponseInfo = await self.access_manager.make_request(request_info)
        duplicates: list[UniqueURLDuplicateInfo] = [
            UniqueURLDuplicateInfo(**entry) for entry in response_info.data["duplicates"]
        ]
        is_duplicate: bool = (len(duplicates) != 0)
        return is_duplicate
