from typing import Sequence

from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.contributions.leaderboard.response import ContributionsLeaderboardResponse, \
    ContributionsLeaderboardInnerResponse
from src.api.endpoints.contributions.shared.contributions import ContributionsCTEContainer
from src.db.helpers.session import session_helper as sh
from src.db.queries.base.builder import QueryBuilderBase


class GetContributionsLeaderboardQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> ContributionsLeaderboardResponse:
        cte = ContributionsCTEContainer()

        query = (
            select(
                cte.user_id,
                cte.count,
            )
            .order_by(
                cte.count.desc()
            )
        )

        mappings: Sequence[RowMapping] = await sh.mappings(session, query=query)
        inner_responses = [
            ContributionsLeaderboardInnerResponse(
                user_id=mapping["user_id"],
                count=mapping["count"]
            )
            for mapping in mappings
        ]

        return ContributionsLeaderboardResponse(
            leaderboard=inner_responses
        )