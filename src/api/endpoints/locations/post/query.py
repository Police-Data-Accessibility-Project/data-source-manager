from typing import Any

from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.locations.post.request import AddLocationRequestModel
from src.api.endpoints.locations.post.response import AddLocationResponseModel
from src.db import Locality, Location
from src.db.queries.base.builder import QueryBuilderBase


class AddLocationQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        request: AddLocationRequestModel
    ):
        super().__init__()
        self.request = request

    async def run(self, session: AsyncSession) -> AddLocationResponseModel:
        locality = Locality(
            name=self.request.locality_name,
            county_id=self.request.county_id
        )
        session.add(locality)
        await session.flush()
        locality_id: int = locality.id

        query = (
            select(
                Location.id
            )
            .where(
                Location.locality_id == locality_id
            )
        )

        mapping: RowMapping = await self.sh.mapping(
            session=session,
            query=query
        )

        return AddLocationResponseModel(
            location_id=mapping[Location.id]
        )
