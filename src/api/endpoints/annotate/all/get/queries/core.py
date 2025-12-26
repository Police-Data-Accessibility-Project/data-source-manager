from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate._shared.extract import extract_and_format_get_annotation_result
from src.api.endpoints.annotate._shared.queries import helper
from src.api.endpoints.annotate.all.get.models.response import GetNextURLForAllAnnotationResponse
from src.api.endpoints.annotate.all.get.queries.features.followed_by_any_user import get_followed_by_any_user_feature
from src.api.endpoints.annotate.all.get.queries.features.followed_by_user import get_followed_by_user_feature
from src.api.endpoints.annotate.all.get.queries.helpers import not_exists_user_annotation
from src.db.models.impl.annotation.agency.user.sqlalchemy import AnnotationAgencyUser
from src.db.models.impl.annotation.location.user.sqlalchemy import AnnotationLocationUser
from src.db.models.impl.annotation.record_type.user.user import AnnotationRecordTypeUser
from src.db.models.impl.annotation.url_type.user.sqlalchemy import AnnotationURLTypeUser
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase


class GetNextURLForAllAnnotationQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        batch_id: int | None,
        user_id: int,
        url_id: int | None = None
    ):
        super().__init__()
        self.batch_id = batch_id
        self.url_id = url_id
        self.user_id = user_id

    async def run(
        self,
        session: AsyncSession
    ) -> GetNextURLForAllAnnotationResponse:
        base_cte = select(
            URL.id,
            get_followed_by_user_feature(self.user_id),
            get_followed_by_any_user_feature()
        ).cte("base")

        query = select(
            URL,
            base_cte.c.followed_by_user,
            base_cte.c.followed_by_any_user,
        ).join(
            base_cte,
            base_cte.c.id == URL.id
        )
        query = helper.add_joins(query)

        # Add user annotation-specific joins and conditions
        if self.batch_id is not None:
            query = query.join(LinkBatchURL).where(LinkBatchURL.batch_id == self.batch_id)
        if self.url_id is not None:
            query = query.where(URL.id == self.url_id)

        user_models = [
            AnnotationURLTypeUser,
            AnnotationAgencyUser,
            AnnotationLocationUser,
            AnnotationRecordTypeUser,
        ]

        query = (
            query
            .where(
                    # Must not have been previously annotated by user
                *[
                    not_exists_user_annotation(
                        user_id=self.user_id,
                        user_model=user_model
                    )
                    for user_model in user_models
                ]
            )
        )


        # Conclude query with limit and sorting
        query = helper.add_common_where_conditions(query)
        query = helper.add_load_options(query)
        query = (
            # Sorting Priority
            query.order_by(
                # If the specific user follows *this* location, privilege it
                helper.bool_sort(base_cte.c.followed_by_user),
                *helper.common_sorts(base_cte)
            )
            # Limit to 1 result
            .limit(1)
        )

        raw_results = (await session.execute(query)).unique()
        url: URL | None = raw_results.scalars().one_or_none()
        if url is None:
            return GetNextURLForAllAnnotationResponse(
                next_annotation=None
            )

        return await extract_and_format_get_annotation_result(session, url=url, batch_id=self.batch_id)

