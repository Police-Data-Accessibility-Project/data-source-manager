
from sqlalchemy import Select
from starlette.exceptions import HTTPException
from starlette.status import HTTP_400_BAD_REQUEST

from src.api.endpoints.review.enums import RejectionReason
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.reviewing_user import ReviewingUserURL
from src.db.queries.base.builder import QueryBuilderBase


class RejectURLQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        url_id: int,
        user_id: int,
        rejection_reason: RejectionReason
    ):
        super().__init__()
        self.url_id = url_id
        self.user_id = user_id
        self.rejection_reason = rejection_reason

    async def run(self, session) -> None:

        query = (
            Select(URL)
            .where(URL.id == self.url_id)
        )

        url = await session.execute(query)
        url = url.scalars().first()

        validation_type: URLType
        match self.rejection_reason:
            case RejectionReason.INDIVIDUAL_RECORD:
                validation_type = URLType.INDIVIDUAL_RECORD
            case RejectionReason.BROKEN_PAGE_404:
                validation_type = URLType.BROKEN_PAGE
            case RejectionReason.NOT_RELEVANT:
                validation_type = URLType.NOT_RELEVANT
            case _:
                raise HTTPException(
                    status_code=HTTP_400_BAD_REQUEST,
                    detail="Invalid rejection reason"
                )

        flag_url_validated = FlagURLValidated(
            url_id=self.url_id,
            type=validation_type
        )
        session.add(flag_url_validated)

        # Add rejecting user
        rejecting_user_url = ReviewingUserURL(
            user_id=self.user_id,
            url_id=self.url_id
        )

        session.add(rejecting_user_url)