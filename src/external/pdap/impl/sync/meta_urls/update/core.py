from src.external.pdap._templates.request_builder import PDAPRequestBuilderBase
from src.external.pdap.impl.sync.meta_urls.update.request import UpdateMetaURLsOuterRequest


class UpdateMetaURLsRequestBuilder(PDAPRequestBuilderBase):

    def __init__(
        self,
        request: UpdateMetaURLsOuterRequest
    ):
        super().__init__()
        self.request = request

    async def inner_logic(self) -> None:
        url: str = self.build_url("v3/sync/meta-urls/update")
        await self.post(
            url=url,
            model=self.request
        )