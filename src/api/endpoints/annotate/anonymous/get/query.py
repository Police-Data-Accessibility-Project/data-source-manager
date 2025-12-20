from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate._shared.extract import extract_and_format_get_annotation_result
from src.api.endpoints.annotate._shared.queries import helper
from src.api.endpoints.annotate.all.get.models.response import GetNextURLForAllAnnotationResponse
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
        session_id: UUID
    ):
        super().__init__()
        self.session_id = session_id

    async def run(self, session: AsyncSession) -> GetNextURLForAnonymousAnnotationResponse:
        query = helper.get_select()

        # Add anonymous annotation-specific conditions.
        query = (
            query
            .where(
                # Must not have been previously annotated by user
                not_exists_anon_annotation(
                    session_id=self.session_id,
                    anon_model=AnnotationURLTypeAnon
                ),
                not_exists_anon_annotation(
                    session_id=self.session_id,
                    anon_model=AnnotationRecordTypeAnon
                ),
                not_exists_anon_annotation(
                    session_id=self.session_id,
                    anon_model=AnnotationLocationAnon
                ),
                not_exists_anon_annotation(
                    session_id=self.session_id,
                    anon_model=AnnotationAgencyAnon
                )
            )
        )
        query = helper.conclude(query)

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
