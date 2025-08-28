from sqlalchemy.ext.asyncio import AsyncSession

from src.db.queries.base.builder import QueryBuilderBase


class UpdateMetaURLsQueryBuilder(QueryBuilderBase):
    """Update meta URLs in DB

    Meta URLs should be given a validation status as a Meta URL
    and have their record type updated to CONTACT_INFO_AND_AGENCY_META
    """

    async def run(self, session: AsyncSession) -> None:
        raise NotImplementedError