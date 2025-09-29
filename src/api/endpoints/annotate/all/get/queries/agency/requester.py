from typing import Sequence

from sqlalchemy import func, select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate.all.get.models.agency import AgencyAnnotationAutoSuggestion, \
    AgencyAnnotationUserSuggestion
from src.api.endpoints.annotate.all.get.queries.agency.suggestions_with_highest_confidence import \
    SuggestionsWithHighestConfidenceCTE
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.link.user_suggestion_not_found.agency.sqlalchemy import LinkUserSuggestionAgencyNotFound
from src.db.models.impl.url.suggestion.agency.user import UserUrlAgencySuggestion
from src.db.templates.requester import RequesterBase


class GetAgencySuggestionsRequester(RequesterBase):

    def __init__(self, session: AsyncSession, url_id: int):
        super().__init__(session)
        self.url_id = url_id

    async def get_user_agency_suggestions(self) -> list[AgencyAnnotationUserSuggestion]:
        query = (
            select(
                UserUrlAgencySuggestion.agency_id,
                func.count(UserUrlAgencySuggestion.user_id).label("count"),
                Agency.name.label("agency_name"),
            )
            .join(
                Agency,
                Agency.agency_id == UserUrlAgencySuggestion.agency_id
            )
            .where(
                UserUrlAgencySuggestion.url_id == self.url_id
            )
            .group_by(
                UserUrlAgencySuggestion.agency_id,
                Agency.name
            )
            .order_by(
                func.count(UserUrlAgencySuggestion.user_id).desc()
            )
            .limit(3)
        )

        results: Sequence[RowMapping] = await sh.mappings(self.session, query=query)

        return [
            AgencyAnnotationUserSuggestion(
                agency_id=autosuggestion["agency_id"],
                user_count=autosuggestion["count"],
                agency_name=autosuggestion["agency_name"],
            )
            for autosuggestion in results
        ]


    async def get_auto_agency_suggestions(self) -> list[AgencyAnnotationAutoSuggestion]:
        cte = SuggestionsWithHighestConfidenceCTE()
        query = (
            select(
                cte.agency_id,
                cte.confidence,
                Agency.name.label("agency_name"),
            )
            .outerjoin(
                Agency,
                Agency.agency_id == cte.agency_id
            )
            .where(
                cte.url_id == self.url_id
            )
            .order_by(
                cte.confidence.desc()
            )
            .limit(3)
        )

        results: Sequence[RowMapping] = await sh.mappings(self.session, query=query)

        return [
            AgencyAnnotationAutoSuggestion(
                agency_id=autosuggestion["agency_id"],
                confidence=autosuggestion["confidence"],
                agency_name=autosuggestion["agency_name"],
            )
            for autosuggestion in results
        ]

    async def get_not_found_count(self) -> int:
        query = (
            select(
                func.count(LinkUserSuggestionAgencyNotFound.user_id)
            )
            .where(
                LinkUserSuggestionAgencyNotFound.url_id == self.url_id
            )
        )

        return await sh.scalar(self.session, query=query)