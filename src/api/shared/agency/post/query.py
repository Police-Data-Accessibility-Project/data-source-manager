from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.queries.base.builder import QueryBuilderBase


class AddURLAgencyLinkQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        url_id: int,
        agency_id: int
    ):
        super().__init__()
        self.url_id = url_id
        self.agency_id = agency_id

    async def run(self, session: AsyncSession) -> None:
        link = LinkURLAgency(
            url_id=self.url_id,
            agency_id=self.agency_id
        )
        session.add(link)
        try:
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to add URL agency link: {e}"
            )