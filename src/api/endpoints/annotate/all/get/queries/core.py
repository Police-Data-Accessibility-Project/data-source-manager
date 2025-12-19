from sqlalchemy import Select, exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.api.endpoints.annotate._shared.extract import extract_and_format_get_annotation_result
from src.api.endpoints.annotate.all.get.models.response import GetNextURLForAllAnnotationResponse
from src.collectors.enums import URLStatus
from src.db.models.impl.annotation.agency.user.sqlalchemy import AnnotationAgencyUser
from src.db.models.impl.annotation.location.user.sqlalchemy import AnnotationLocationUser
from src.db.models.impl.flag.url_suspended.sqlalchemy import FlagURLSuspended
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.annotation.record_type.user.user import AnnotationUserRecordType
from src.db.models.impl.annotation.url_type.user.sqlalchemy import AnnotationUserURLType
from src.db.models.views.unvalidated_url import UnvalidatedURL
from src.db.models.views.url_anno_count import URLAnnotationCount
from src.db.models.views.url_annotations_flags import URLAnnotationFlagsView
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
        )
        if self.batch_id is not None:
            query = query.join(LinkBatchURL).where(LinkBatchURL.batch_id == self.batch_id)
        if self.url_id is not None:
            query = query.where(URL.id == self.url_id)
        query = (
            query
            .where(
                    URL.status == URLStatus.OK.value,
                    # Must not have been previously annotated by user
                    ~exists(
                        select(AnnotationUserURLType.url_id)
                        .where(
                            AnnotationUserURLType.url_id == URL.id,
                            AnnotationUserURLType.user_id == self.user_id,
                        )
                    ),
                    ~exists(
                        select(AnnotationAgencyUser.url_id)
                        .where(
                            AnnotationAgencyUser.url_id == URL.id,
                            AnnotationAgencyUser.user_id == self.user_id,
                        )
                    ),
                    ~exists(
                        select(
                            AnnotationLocationUser.url_id
                        )
                        .where(
                            AnnotationLocationUser.url_id == URL.id,
                            AnnotationLocationUser.user_id == self.user_id,
                        )
                    ),
                    ~exists(
                        select(
                            AnnotationUserRecordType.url_id
                        )
                        .where(
                            AnnotationUserRecordType.url_id == URL.id,
                            AnnotationUserRecordType.user_id == self.user_id,
                        )
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
        )
        # Add load options
        query = query.options(
            joinedload(URL.html_content),
            joinedload(URL.user_relevant_suggestions),
            joinedload(URL.user_record_type_suggestions),
            joinedload(URL.name_suggestions),
        )

        query = query.order_by(
            URLAnnotationCount.total_anno_count.desc(),
            URL.id.asc()
        ).limit(1)
        raw_results = (await session.execute(query)).unique()
        url: URL | None = raw_results.scalars().one_or_none()
        if url is None:
            return GetNextURLForAllAnnotationResponse(
                next_annotation=None
            )

        return await extract_and_format_get_annotation_result(session, url=url, batch_id=self.batch_id)

