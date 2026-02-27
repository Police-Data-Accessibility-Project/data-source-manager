from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate.missing.post.models import ResolveMissingAnnotationRequest
from src.api.shared.models.message_response import MessageResponse
from src.db.models.impl.annotation.agency.user.sqlalchemy import AnnotationAgencyUser
from src.db.models.impl.annotation.location.user.sqlalchemy import AnnotationLocationUser
from src.db.models.impl.flag.url_suspended.sqlalchemy import FlagURLSuspended
from src.db.models.impl.link.user_suggestion_not_found.agency.sqlalchemy import LinkUserSuggestionAgencyNotFound
from src.db.models.impl.link.user_suggestion_not_found.location.sqlalchemy import LinkUserSuggestionLocationNotFound
from src.db.queries.base.builder import QueryBuilderBase


class ResolveMissingAnnotationQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        user_id: int,
        url_id: int,
        post_info: ResolveMissingAnnotationRequest,
    ):
        super().__init__()
        self.user_id = user_id
        self.url_id = url_id
        self.post_info = post_info

    async def run(
        self,
        session: AsyncSession
    ) -> MessageResponse:
        existing_location_annotation = (
            await session.execute(
                select(AnnotationLocationUser)
                .where(
                    AnnotationLocationUser.url_id == self.url_id,
                    AnnotationLocationUser.user_id == self.user_id,
                    AnnotationLocationUser.location_id == self.post_info.location_id,
                )
            )
        ).scalar_one_or_none()
        if existing_location_annotation is None:
            session.add(
                AnnotationLocationUser(
                    url_id=self.url_id,
                    user_id=self.user_id,
                    location_id=self.post_info.location_id,
                )
            )

        existing_agency_annotation = (
            await session.execute(
                select(AnnotationAgencyUser)
                .where(
                    AnnotationAgencyUser.url_id == self.url_id,
                    AnnotationAgencyUser.user_id == self.user_id,
                    AnnotationAgencyUser.agency_id == self.post_info.agency_id,
                )
            )
        ).scalar_one_or_none()
        if existing_agency_annotation is None:
            session.add(
                AnnotationAgencyUser(
                    url_id=self.url_id,
                    user_id=self.user_id,
                    agency_id=self.post_info.agency_id,
                )
            )

        await session.execute(
            delete(LinkUserSuggestionLocationNotFound).where(
                LinkUserSuggestionLocationNotFound.url_id == self.url_id
            )
        )
        await session.execute(
            delete(LinkUserSuggestionAgencyNotFound).where(
                LinkUserSuggestionAgencyNotFound.url_id == self.url_id
            )
        )
        await session.execute(
            delete(FlagURLSuspended).where(
                FlagURLSuspended.url_id == self.url_id
            )
        )

        return MessageResponse(
            message="Missing location/agency annotations resolved."
        )
