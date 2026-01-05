from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate._shared.extract import extract_and_format_get_annotation_result
from src.api.endpoints.annotate._shared.queries import helper
from src.api.endpoints.annotate._shared.queries.helper import add_common_where_conditions, add_load_options, \
    common_sorts
from src.api.endpoints.annotate.all.get.models.response import GetNextURLForAllAnnotationResponse
from src.api.endpoints.annotate.all.get.queries.features.followed_by_any_user import get_followed_by_any_user_feature
from src.api.endpoints.annotate.anonymous.get.helpers import not_exists_anon_annotation
from src.api.endpoints.annotate.anonymous.get.response import GetNextURLForAnonymousAnnotationResponse
from src.db.models.impl.annotation.agency.anon.sqlalchemy import AnnotationAgencyAnon
from src.db.models.impl.annotation.location.anon.sqlalchemy import AnnotationLocationAnon
from src.db.models.impl.annotation.record_type.anon.sqlalchemy import AnnotationRecordTypeAnon
from src.db.models.impl.annotation.url_type.anon.sqlalchemy import AnnotationURLTypeAnon
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase


class GetNextURLForAnonymousAnnotationQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        session_id: UUID,
        offset: int | None = None
    ):
        super().__init__()
        self.session_id = session_id
        self.offset = offset

    async def run(self, session: AsyncSession) -> GetNextURLForAnonymousAnnotationResponse:
        base_cte = select(
            URL.id,
            get_followed_by_any_user_feature()
        ).cte("base")

        query = select(
            URL,
            base_cte.c.followed_by_any_user,
        ).join(
            base_cte,
            base_cte.c.id == URL.id
        )
        query = helper.add_joins(query)

        anon_models = [
            AnnotationURLTypeAnon,
            AnnotationRecordTypeAnon,
            AnnotationLocationAnon,
            AnnotationAgencyAnon
        ]

        # Add anonymous annotation-specific conditions.
        query = (
            query
            .where(
                # Must not have been previously annotated by user
                *[
                    not_exists_anon_annotation(
                        session_id=self.session_id,
                        anon_model=anon_model
                    )
                    for anon_model in anon_models
                ]
            )
        )
        query = add_common_where_conditions(query)
        query = add_load_options(query)
        if self.offset is not None:
            offset = 0
        else:
            offset = self.offset

        query = (
            # Sorting Priority
            query.order_by(
                *common_sorts(base_cte)
            )
            .offset(offset)
            # Limit to 1 result
            .limit(1)
        )

        raw_results = (await session.execute(query)).unique()
        url: URL | None = raw_results.scalars().one_or_none()
        if url is None:
            return GetNextURLForAnonymousAnnotationResponse(
                next_annotation=None,
                session_id=self.session_id
            )

        response: GetNextURLForAllAnnotationResponse = await extract_and_format_get_annotation_result(session, url=url)
        return GetNextURLForAnonymousAnnotationResponse(
            session_id=self.session_id,
            next_annotation=response.next_annotation
        )
