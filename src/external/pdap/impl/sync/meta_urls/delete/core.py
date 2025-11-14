from pdap_access_manager import AccessManager

from src.external.pdap._templates.request_builder import PDAPRequestBuilderBase
from src.external.pdap.impl.sync.shared.models.delete.request import DSAppSyncDeleteRequestModel


class DeleteMetaURLsRequestBuilder(PDAPRequestBuilderBase):

    def __init__(
        self,
        ds_app_ids: list[int]
    ):
        super().__init__()
        self.ds_app_ids = ds_app_ids

    async def inner_logic(self) -> None:
        url: str = self.build_url("v3/source-manager/meta-urls/delete")
        await self.post(
            url=url,
            model=DSAppSyncDeleteRequestModel(
                ids=self.ds_app_ids
            )
        )

