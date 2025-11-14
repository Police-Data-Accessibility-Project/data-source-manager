from abc import ABC, abstractmethod
from http import HTTPStatus
from typing import Any

from pdap_access_manager.access_manager.async_ import AccessManagerAsync
from pdap_access_manager.enums import RequestType
from pdap_access_manager.models.request import RequestInfo
from pdap_access_manager.models.response import ResponseInfo
from pydantic import BaseModel


class PDAPRequestBuilderBase(ABC):

    def __init__(self):
        self.access_manager: AccessManagerAsync | None = None

    async def run(self, access_manager: AccessManagerAsync) -> Any:
        self.access_manager = access_manager
        return await self.inner_logic()

    def build_url(self, path: str) -> str:
        return f"{self.access_manager.data_sources_url}/{path}"

    async def post(
        self,
        url: str,
        model: BaseModel
    ) -> dict:
        request_info = RequestInfo(
            type_=RequestType.POST,
            url=url,
            json_=model.model_dump(mode='json'),
            headers=await self.access_manager.jwt_header()
        )
        response_info: ResponseInfo = await self.access_manager.make_request(request_info)
        if response_info.status_code != HTTPStatus.OK:
            raise Exception(f"Failed to make request to PDAP: {response_info.data}")
        return response_info.data

    @abstractmethod
    async def inner_logic(self) -> Any:
        raise NotImplementedError
