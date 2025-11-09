from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.meta_url.by_id.put.request import UpdateMetaURLRequest
from src.api.shared.batch.url.link import UpdateBatchURLLinkQueryBuilder
from src.api.shared.url.put.query import UpdateURLQueryBuilder
from src.db.queries.base.builder import QueryBuilderBase


class UpdateMetaURLQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        url_id: int,
        request: UpdateMetaURLRequest
    ):
        super().__init__()
        self.url_id = url_id
        self.request = request

    async def run(self, session: AsyncSession) -> None:

        # Update Batch ID if not none
        if self.request.batch_id is not None:
            await UpdateBatchURLLinkQueryBuilder(
                batch_id=self.request.batch_id,
                url_id=self.url_id
            ).run(session)


        # Update URL if any of the URL fields are not None
        if (
            self.request.description is None and
            self.request.name is None and
            self.request.description is None
        ):
            return

        await UpdateURLQueryBuilder(
            url_id=self.url_id,
            url=self.request.url,
            name=self.request.name,
            description=self.request.description,
        ).run(
            session,
        )

