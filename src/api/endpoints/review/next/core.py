from sqlalchemy import FromClause, select, Select, desc, asc, func, CTE
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.api.endpoints.review.next.convert import convert_agency_info_to_final_review_annotation_agency_info
from src.api.endpoints.review.next.dto import FinalReviewOptionalMetadata, FinalReviewBatchInfo, \
    GetNextURLForFinalReviewOuterResponse, GetNextURLForFinalReviewResponse, FinalReviewAnnotationInfo
from src.api.endpoints.review.next.extract import extract_html_content_infos, extract_optional_metadata
from src.api.endpoints.review.next.queries.count_reviewed import COUNT_REVIEWED_CTE
from src.api.endpoints.review.next.queries.eligible_urls import build_eligible_urls_cte
from src.api.endpoints.review.next.templates.count_cte import CountCTE
from src.collectors.enums import URLStatus
from src.core.tasks.url.operators.html.scraper.parser.util import convert_to_response_html_info
from src.db.constants import USER_ANNOTATION_MODELS
from src.db.dto_converter import DTOConverter
from src.db.dtos.url.html_content import URLHTMLContentInfo
from src.db.exceptions import FailedQueryException
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.suggestion.agency.subtask.sqlalchemy import URLAutoAgencyIDSubtask
from src.db.models.impl.url.suggestion.agency.suggestion.sqlalchemy import AgencyIDSubtaskSuggestion
from src.db.models.impl.url.suggestion.agency.user import UserUrlAgencySuggestion
from src.db.queries.base.builder import QueryBuilderBase
from src.db.queries.implementations.core.common.annotation_exists_.core import AnnotationExistsCTEQueryBuilder

TOTAL_DISTINCT_ANNOTATION_COUNT_LABEL = "total_distinct_annotation_count"


class GetNextURLForFinalReviewQueryBuilder(QueryBuilderBase):

    def __init__(self, batch_id: int | None = None):
        super().__init__()
        self.batch_id = batch_id
        self.anno_exists_builder = AnnotationExistsCTEQueryBuilder()
        # The below relationships are joined directly to the URL
        self.single_join_relationships = [
            URL.html_content,
            URL.auto_record_type_suggestion,
            URL.auto_relevant_suggestion,
            URL.user_relevant_suggestions,
            URL.user_record_type_suggestions,
            URL.optional_data_source_metadata,
        ]
        # The below relationships are joined to entities that are joined to the URL
        self.double_join_relationships = [
            (URL.user_agency_suggestions, UserUrlAgencySuggestion.agency),
            (URL.confirmed_agencies, LinkURLAgency.agency)
        ]

        self.count_label = "count"

    def _get_where_exist_clauses(
        self,
        query: FromClause,
    ):
        where_clauses = []
        for model in USER_ANNOTATION_MODELS:
            label = self.anno_exists_builder.get_exists_label(model)
            where_clause = getattr(query.c, label) == 1
            where_clauses.append(where_clause)
        return where_clauses

    def _build_base_query(self) -> Select:
        eligible_urls: CTE = build_eligible_urls_cte(batch_id=self.batch_id)

        query = (
            select(
                URL,
            )
            .select_from(
                eligible_urls
            )
            .join(
                URL,
                URL.id == eligible_urls.c.url_id
            )
            .where(
                URL.status == URLStatus.OK.value
            )
        )
        return query

    async def _apply_options(
        self,
        url_query: Select
    ):
        return url_query.options(
            *[
                joinedload(relationship)
                for relationship in self.single_join_relationships
            ],
            *[
                joinedload(primary).joinedload(secondary)
                for primary, secondary in self.double_join_relationships
            ],
            joinedload(URL.auto_agency_subtasks)
            .joinedload(URLAutoAgencyIDSubtask.suggestions)
            .contains_eager(AgencyIDSubtaskSuggestion.agency)
        )


    async def get_batch_info(self, session: AsyncSession) -> FinalReviewBatchInfo | None:
        if self.batch_id is None:
            return None

        count_reviewed_query: CountCTE = COUNT_REVIEWED_CTE

        count_ready_query = await self.get_count_ready_query()

        full_query = (
            select(
                func.coalesce(count_reviewed_query.count, 0).label("count_reviewed"),
                func.coalesce(count_ready_query.c[self.count_label], 0).label("count_ready_for_review")
            )
            .select_from(
                count_ready_query.outerjoin(
                    count_reviewed_query.cte,
                    count_reviewed_query.batch_id == count_ready_query.c.batch_id
                )
            )
        )

        raw_result = await session.execute(full_query)
        return FinalReviewBatchInfo(**raw_result.mappings().one())

    async def get_count_ready_query(self):
        # TODO: Migrate to separate query builder
        builder = self.anno_exists_builder
        count_ready_query = (
            select(
                LinkBatchURL.batch_id,
                func.count(URL.id).label(self.count_label)
            )
            .select_from(LinkBatchURL)
            .join(URL)
            .join(
                builder.query,
                builder.url_id == URL.id
            )
            .where(
                LinkBatchURL.batch_id == self.batch_id,
                URL.status == URLStatus.OK.value,
                *self._get_where_exist_clauses(
                    builder.query
                )
            )
            .group_by(LinkBatchURL.batch_id)
            .subquery("count_ready")
        )
        return count_ready_query

    async def run(
        self,
        session: AsyncSession
    ) -> GetNextURLForFinalReviewOuterResponse:
        await self.anno_exists_builder.build()

        url_query = await self.build_url_query()

        raw_result = await session.execute(url_query.limit(1))
        row = raw_result.unique().first()

        if row is None:
            return GetNextURLForFinalReviewOuterResponse(
                next_source=None,
                remaining=0
            )

        count_query = (
            select(
                func.count()
            ).select_from(url_query.subquery("count"))
        )
        remaining_result = (await session.execute(count_query)).scalar()


        result: URL = row[0]

        html_content_infos: list[URLHTMLContentInfo] = await extract_html_content_infos(result)
        optional_metadata: FinalReviewOptionalMetadata = await extract_optional_metadata(result)

        batch_info = await self.get_batch_info(session)
        try:

            next_source = GetNextURLForFinalReviewResponse(
                id=result.id,
                url=result.url,
                html_info=convert_to_response_html_info(html_content_infos),
                name=result.name,
                description=result.description,
                annotations=FinalReviewAnnotationInfo(
                    relevant=DTOConverter.final_review_annotation_relevant_info(
                        user_suggestions=result.user_relevant_suggestions,
                        auto_suggestion=result.auto_relevant_suggestion
                    ),
                    record_type=DTOConverter.final_review_annotation_record_type_info(
                        user_suggestions=result.user_record_type_suggestions,
                        auto_suggestion=result.auto_record_type_suggestion
                    ),
                    agency=convert_agency_info_to_final_review_annotation_agency_info(
                        subtasks=result.auto_agency_subtasks,
                        user_agency_suggestions=result.user_agency_suggestions,
                        confirmed_agencies=result.confirmed_agencies
                    )
                ),
                optional_metadata=optional_metadata,
                batch_info=batch_info
            )
            return GetNextURLForFinalReviewOuterResponse(
                next_source=next_source,
                remaining=remaining_result
            )
        except Exception as e:
            raise FailedQueryException(f"Failed to convert result for url id {result.id} to response") from e

    async def build_url_query(self):
        url_query = self._build_base_query()
        url_query = await self._apply_options(url_query)

        return url_query
