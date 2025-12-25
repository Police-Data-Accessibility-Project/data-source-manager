from src.external.pdap._templates.request_builder import PDAPRequestBuilderBase
from src.external.pdap.impl.sync.follows.response import SyncFollowGetInnerResponse, SyncFollowGetOuterResponse


class GetFollowsRequestBuilder(PDAPRequestBuilderBase):

    async def inner_logic(self) -> list[SyncFollowGetInnerResponse]:
        url: str = self.build_url("v3/sync/follows")
        response: SyncFollowGetOuterResponse = await self.get(
            url=url,
            model=SyncFollowGetOuterResponse
        )
        return response.follows
