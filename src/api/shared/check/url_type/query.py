from fastapi import HTTPException
from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase


class CheckURLTypeQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        url_id: int,
        url_type: URLType
    ):
        super().__init__()
        self.url_id = url_id
        self.url_type = url_type

    async def run(self, session: AsyncSession) -> None:
        """
        Raises:
            Bad Request if url_type is not valid or does not exist
        """

        query = (
            select(
                URL.id,
                FlagURLValidated.type
            )
            .outerjoin(
                FlagURLValidated,
                FlagURLValidated.url_id == URL.id
            )
            .where(
                URL.id == self.url_id,
            )
        )

        result: RowMapping | None = await self.sh.mapping(session, query=query)
        if result is None:
            raise HTTPException(
                status_code=404,
                detail="URL not found"
            )
        url_type: URLType | None = result.get("type")
        if url_type is None:
            raise HTTPException(
                status_code=400,
                detail="URL is not validated"
            )
        if url_type != self.url_type:
            raise HTTPException(
                status_code=400,
                detail="URL type does not match expected URL type"
            )