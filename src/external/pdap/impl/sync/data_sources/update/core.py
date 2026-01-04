from src.external.pdap._templates.request_builder import PDAPRequestBuilderBase
from src.external.pdap.impl.sync.data_sources.update.request import UpdateDataSourcesOuterRequest


class UpdateDataSourcesRequestBuilder(PDAPRequestBuilderBase):

    def __init__(
        self,
        request: UpdateDataSourcesOuterRequest
    ):
        super().__init__()
        self.request = request

    async def inner_logic(self) -> None:
        url: str = self.build_url("v3/sync/data-sources/update")
        await self.post(
            url=url,
            model=self.request
        )