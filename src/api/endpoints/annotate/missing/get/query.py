from typing import Sequence

from sqlalchemy import select, RowMapping, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate.missing.get.models import MissingAnnotationQueueEntry, MissingAnnotationQueueResponse
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.flag.url_suspended.sqlalchemy import FlagURLSuspended
from src.db.models.impl.link.user_suggestion_not_found.agency.sqlalchemy import LinkUserSuggestionAgencyNotFound
from src.db.models.impl.link.user_suggestion_not_found.location.sqlalchemy import LinkUserSuggestionLocationNotFound
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.views.unvalidated_url import UnvalidatedURL
from src.db.queries.base.builder import QueryBuilderBase


class GetMissingAnnotationQueueQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        limit: int = 200,
    ):
        super().__init__()
        self.limit = limit

    async def run(
        self,
        session: AsyncSession
    ) -> MissingAnnotationQueueResponse:
        location_count_subquery = (
            select(
                func.count(LinkUserSuggestionLocationNotFound.user_id)
            )
            .where(
                LinkUserSuggestionLocationNotFound.url_id == URL.id
            )
            .scalar_subquery()
        )

        agency_count_subquery = (
            select(
                func.count(LinkUserSuggestionAgencyNotFound.user_id)
            )
            .where(
                LinkUserSuggestionAgencyNotFound.url_id == URL.id
            )
            .scalar_subquery()
        )

        query = (
            select(
                URL.id.label("url_id"),
                URL.full_url.label("url"),
                location_count_subquery.label("missing_location_count"),
                agency_count_subquery.label("missing_agency_count"),
            )
            .join(
                FlagURLSuspended,
                FlagURLSuspended.url_id == URL.id,
            )
            .join(
                UnvalidatedURL,
                UnvalidatedURL.url_id == URL.id,
            )
            .where(
                or_(
                    location_count_subquery >= 2,
                    agency_count_subquery >= 2,
                )
            )
            .order_by(URL.id.asc())
            .limit(self.limit)
        )

        mappings: Sequence[RowMapping] = await sh.mappings(
            session=session,
            query=query,
        )

        return MissingAnnotationQueueResponse(
            entries=[
                MissingAnnotationQueueEntry(
                    **mapping,
                )
                for mapping in mappings
            ]
        )
