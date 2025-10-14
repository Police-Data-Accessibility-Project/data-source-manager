from typing import Any

from sqlalchemy import Select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.api.endpoints.annotate._shared.extract import extract_and_format_get_annotation_result
from src.api.endpoints.annotate.all.get.models.response import GetNextURLForAllAnnotationResponse
from src.collectors.enums import URLStatus
from src.db.helpers.query import not_exists_url
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.suggestion.anonymous.url_type.sqlalchemy import AnonymousAnnotationURLType
from src.db.models.views.unvalidated_url import UnvalidatedURL
from src.db.models.views.url_anno_count import URLAnnotationCount
from src.db.models.views.url_annotations_flags import URLAnnotationFlagsView
from src.db.queries.base.builder import QueryBuilderBase


class GetNextURLForAnonymousAnnotationQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> GetNextURLForAllAnnotationResponse:

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
                not_exists_url(AnonymousAnnotationURLType)
            )
            .options(
                joinedload(URL.html_content),
                joinedload(URL.user_relevant_suggestions),
                joinedload(URL.user_record_type_suggestions),
                joinedload(URL.name_suggestions),
            )
            .order_by(
                func.random()
            )
            .limit(1)
        )

        raw_results = (await session.execute(query)).unique()
        url: URL | None = raw_results.scalars().one_or_none()
        if url is None:
            return GetNextURLForAllAnnotationResponse(
                next_annotation=None
            )

        return await extract_and_format_get_annotation_result(session, url=url)
