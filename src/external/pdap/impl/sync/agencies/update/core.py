from src.external.pdap._templates.request_builder import PDAPRequestBuilderBase
from src.external.pdap.impl.sync.agencies.update.request import UpdateAgenciesOuterRequest


class UpdateAgenciesRequestBuilder(PDAPRequestBuilderBase):

    def __init__(
        self,
        request: UpdateAgenciesOuterRequest
    ):
        super().__init__()
        self.request = request

    async def inner_logic(self) -> None:
        url: str = self.build_url("v3/sync/agencies/update")
        await self.post(
            url=url,
            model=self.request
        )