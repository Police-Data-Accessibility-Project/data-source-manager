from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.url.ds_meta_url.sqlalchemy import DSAppLinkMetaURL
from src.db.queries.base.builder import QueryBuilderBase
from src.external.pdap.impl.sync.shared.models.add.response import DSAppSyncAddResponseInnerModel


class DSAppSyncMetaURLsAddInsertLinksQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        mappings: list[DSAppSyncAddResponseInnerModel]
    ):
        super().__init__()
        self._mappings = mappings

    async def run(self, session: AsyncSession) -> None:
        inserts: list[DSAppLinkMetaURL] = []
        for mapping in self._mappings:
            inserts.append(
                DSAppLinkMetaURL(
                    ds_meta_url_id=mapping.app_id,
                    url_id=mapping.request_id,
                )
            )
        session.add_all(inserts)