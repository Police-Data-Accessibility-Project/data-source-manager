from src.external.pdap._templates.request_builder import PDAPRequestBuilderBase
from src.external.pdap.impl.sync.data_sources.add.request import AddDataSourcesOuterRequest
from src.external.pdap.impl.sync.shared.models.add.response import DSAppSyncAddResponseInnerModel, \
    DSAppSyncAddResponseModel


class AddDataSourcesRequestBuilder(PDAPRequestBuilderBase):

    def __init__(
        self,
        request: AddDataSourcesOuterRequest
    ):
        super().__init__()
        self.request = request

    async def inner_logic(self) -> list[DSAppSyncAddResponseInnerModel]:
        url: str = self.build_url("v3/sync/data-sources/add")
        raw_results = await self.post(
            url=url,
            model=self.request,
        )
        response = DSAppSyncAddResponseModel(**raw_results)
        return response.entities

