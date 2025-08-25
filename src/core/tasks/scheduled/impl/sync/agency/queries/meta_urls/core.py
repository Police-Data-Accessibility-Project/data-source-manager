from sqlalchemy.ext.asyncio import AsyncSession

from src.db.queries.base.builder import QueryBuilderBase
from src.external.pdap.dtos.sync.agencies import AgenciesSyncResponseInnerInfo


class UpdateMetaUrlsQueryBuilder(QueryBuilderBase):
    """Updates meta URLs for agencies."""

    def __init__(self, agencies: list[AgenciesSyncResponseInnerInfo]):
        super().__init__()
        self.agencies = agencies

    async def run(self, session: AsyncSession) -> None:

        # Get existing meta URLs

        # Compare with new meta URLs, separate into add, remove, and do nothing

        # Add new meta URLs

        # Remove old meta URLs