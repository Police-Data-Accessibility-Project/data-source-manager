from typing import Any
from uuid import UUID

from sqlalchemy import Select, func, exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.api.endpoints.annotate._shared.extract import extract_and_format_get_annotation_result
from src.api.endpoints.annotate.all.get.models.response import GetNextURLForAllAnnotationResponse
from src.api.endpoints.annotate.anonymous.get.helpers import not_exists_anon_annotation
from src.api.endpoints.annotate.anonymous.get.response import GetNextURLForAnonymousAnnotationResponse
from src.collectors.enums import URLStatus
from src.db.helpers.query import not_exists_url
from src.db.models.impl.flag.url_suspended.sqlalchemy import FlagURLSuspended
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.suggestion.anonymous.agency.sqlalchemy import AnonymousAnnotationAgency
from src.db.models.impl.url.suggestion.anonymous.location.sqlalchemy import AnonymousAnnotationLocation
from src.db.models.impl.url.suggestion.anonymous.record_type.sqlalchemy import AnonymousAnnotationRecordType
from src.db.models.impl.url.suggestion.anonymous.url_type.sqlalchemy import AnonymousAnnotationURLType
from src.db.models.views.unvalidated_url import UnvalidatedURL
from src.db.models.views.url_anno_count import URLAnnotationCount
from src.db.models.views.url_annotations_flags import URLAnnotationFlagsView
from src.db.queries.base.builder import QueryBuilderBase


class GetNextURLForAnonymousAnnotationQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        session_id: UUID
    ):
        super().__init__()
        self.session_id = session_id

    async def run(self, session: AsyncSession) -> GetNextURLForAnonymousAnnotationResponse:

        query = (
            Select(URL)
            # URL Must be unvalidated
            .join(
                UnvalidatedURL,
                UnvalidatedURL.url_id == URL.id
            )
            .join(
                URLAnnotationFlagsView,
                URLAnnotationFlagsView.url_id == URL.id
            )
            .join(
                URLAnnotationCount,
                URLAnnotationCount.url_id == URL.id
            )
            .where(
                URL.status == URLStatus.OK.value,
                # Must not have been previously annotated by user
                not_exists_anon_annotation(
                    session_id=self.session_id,
                    anon_model=AnonymousAnnotationURLType
                ),
                not_exists_anon_annotation(
                    session_id=self.session_id,
                    anon_model=AnonymousAnnotationRecordType
                ),
                not_exists_anon_annotation(
                    session_id=self.session_id,
                    anon_model=AnonymousAnnotationLocation
                ),
                not_exists_anon_annotation(
                    session_id=self.session_id,
                    anon_model=AnonymousAnnotationAgency
                ),
                ~exists(
                    select(
                        FlagURLSuspended.url_id
                    )
                    .where(
                        FlagURLSuspended.url_id == URL.id,
                    )
                )
            )
            .options(
                joinedload(URL.html_content),
                joinedload(URL.user_relevant_suggestions),
                joinedload(URL.user_record_type_suggestions),
                joinedload(URL.name_suggestions),
            )
            .order_by(
                URLAnnotationCount.total_anno_count.desc(),
                URL.id.asc()
            )
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
