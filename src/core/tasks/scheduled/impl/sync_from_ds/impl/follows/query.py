from typing import Any, Sequence

from sqlalchemy import select, RowMapping, delete, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync_from_ds.impl.follows.models.user_location_pairs import UserLocationPairs
from src.core.tasks.scheduled.impl.sync_from_ds.impl.follows.types import UserID, LocationID
from src.db.models.impl.link.location__user_follow import LinkLocationUserFollow
from src.db.queries.base.builder import QueryBuilderBase

class UpdateFollowsInDBQueryBuilder(QueryBuilderBase):

    def __init__(self, api_pairs: list[UserLocationPairs]):
        super().__init__()
        self.api_pairs = api_pairs

    async def run(self, session: AsyncSession) -> Any:
        db_pairs: list[UserLocationPairs] = await self.get_db_pairs(session)
        api_pairs_set = set(self.api_pairs)
        db_pairs_set = set(db_pairs)
        # Get all pairs that are in the API but not in the DB
        new_pairs = api_pairs_set - db_pairs_set
        # Get all pairs that are in the DB but not in the API
        removed_pairs = db_pairs_set - api_pairs_set

        await self.add_new_links(session, new_pairs)
        await self.remove_links(session, removed_pairs)


    async def get_db_pairs(self, session: AsyncSession) -> list[UserLocationPairs]:
        query = (
            select(
                LinkLocationUserFollow.user_id,
                LinkLocationUserFollow.location_id
            )
        )
        mappings: Sequence[RowMapping] = await self.sh.mappings(session, query=query)
        return [
            UserLocationPairs(
                user_id=mapping[LinkLocationUserFollow.user_id],
                location_id=mapping[LinkLocationUserFollow.location_id]
            )
            for mapping in mappings
        ]

    async def add_new_links(
        self,
        session: AsyncSession,
        pairs: set[UserLocationPairs]
    ) -> None:
        for pair in pairs:
            link = LinkLocationUserFollow(
                user_id=pair.user_id,
                location_id=pair.location_id
            )
            session.add(link)

    async def remove_links(
        self,
        session: AsyncSession,
        removed_pairs: set[UserLocationPairs]
    ) -> None:
        tuples: list[tuple[UserID, LocationID]] = [
            (pair.user_id, pair.location_id)
            for pair in removed_pairs
        ]
        statement = delete(LinkLocationUserFollow).where(
            tuple_(
                LinkLocationUserFollow.user_id,
                LinkLocationUserFollow.location_id,
            ).in_(tuples)
        )
        await session.execute(statement)

