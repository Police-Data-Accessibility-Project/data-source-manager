from sqlalchemy import Select, exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.api.endpoints.annotate._shared.queries.get_annotation_batch_info import GetAnnotationBatchInfoQueryBuilder
from src.api.endpoints.annotate.agency.get.dto import GetNextURLForAgencyAgencyInfo
from src.api.endpoints.annotate.agency.get.queries.agency_suggestion_.core import GetAgencySuggestionsQueryBuilder
from src.api.endpoints.annotate.all.get.models.location import LocationAnnotationResponseOuterInfo
from src.api.endpoints.annotate.all.get.models.name import NameAnnotationSuggestion
from src.api.endpoints.annotate.all.get.models.response import GetNextURLForAllAnnotationResponse, \
    GetNextURLForAllAnnotationInnerResponse
from src.api.endpoints.annotate.all.get.queries.location_.core import GetLocationSuggestionsQueryBuilder
from src.api.endpoints.annotate.all.get.queries.name.core import GetNameSuggestionsQueryBuilder
from src.api.endpoints.annotate.relevance.get.dto import RelevanceAnnotationResponseInfo
from src.collectors.enums import URLStatus
from src.db.dto_converter import DTOConverter
from src.db.dtos.url.mapping import URLMapping
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.suggestion.agency.user import UserUrlAgencySuggestion
from src.db.models.impl.url.suggestion.location.user.sqlalchemy import UserLocationSuggestion
from src.db.models.impl.url.suggestion.record_type.auto import AutoRecordTypeSuggestion
from src.db.models.impl.url.suggestion.record_type.user import UserRecordTypeSuggestion
from src.db.models.impl.url.suggestion.relevant.auto.sqlalchemy import AutoRelevantSuggestion
from src.db.models.impl.url.suggestion.relevant.user import UserURLTypeSuggestion
from src.db.models.views.unvalidated_url import UnvalidatedURL
from src.db.models.views.url_anno_count import URLAnnotationCount
from src.db.models.views.url_annotations_flags import URLAnnotationFlagsView
from src.db.queries.base.builder import QueryBuilderBase


class GetNextURLForAllAnnotationQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        batch_id: int | None,
        user_id: int
    ):
        super().__init__()
        self.batch_id = batch_id
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
        query = (
            query
            .where(
                    URL.status == URLStatus.OK.value,
                    # Must not have been previously annotated by user
                    ~exists(
                        select(UserURLTypeSuggestion.id)
                        .where(
                            UserURLTypeSuggestion.url_id == URL.id,
                            UserURLTypeSuggestion.user_id == self.user_id,
                        )
                    ),
                    ~exists(
                        select(UserUrlAgencySuggestion.id)
                        .where(
                            UserUrlAgencySuggestion.url_id == URL.id,
                            UserUrlAgencySuggestion.user_id == self.user_id,
                        )
                    ),
                    ~exists(
                        select(
                            UserLocationSuggestion.url_id
                        )
                        .where(
                            UserLocationSuggestion.url_id == URL.id,
                            UserLocationSuggestion.user_id == self.user_id,
                        )
                    ),
                    ~exists(
                        select(
                            UserRecordTypeSuggestion.url_id
                        )
                        .where(
                            UserRecordTypeSuggestion.url_id == URL.id,
                            UserRecordTypeSuggestion.user_id == self.user_id,
                        )
                    )
            )
        )
        # Add load options
        query = query.options(
            joinedload(URL.html_content),
            joinedload(URL.auto_relevant_suggestion),
            joinedload(URL.auto_record_type_suggestion),
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

        html_response_info = DTOConverter.html_content_list_to_html_response_info(
            url.html_content
        )

        auto_relevant: AutoRelevantSuggestion | None = None
        if url.auto_relevant_suggestion is not None:
            auto_relevant = url.auto_relevant_suggestion

        auto_record_type: AutoRecordTypeSuggestion | None = None
        if url.auto_record_type_suggestion is not None:
            auto_record_type = url.auto_record_type_suggestion.record_type

        agency_suggestions: list[GetNextURLForAgencyAgencyInfo] = \
            await GetAgencySuggestionsQueryBuilder(url_id=url.id).run(session)
        location_suggestions: LocationAnnotationResponseOuterInfo = \
            await GetLocationSuggestionsQueryBuilder(url_id=url.id).run(session)
        name_suggestions: list[NameAnnotationSuggestion] = \
            await GetNameSuggestionsQueryBuilder(url_id=url.id).run(session)

        return GetNextURLForAllAnnotationResponse(
            next_annotation=GetNextURLForAllAnnotationInnerResponse(
                url_info=URLMapping(
                    url_id=url.id,
                    url=url.url
                ),
                html_info=html_response_info,
                suggested_relevant=RelevanceAnnotationResponseInfo(
                    is_relevant=auto_relevant.relevant,
                    confidence=auto_relevant.confidence,
                    model_name=auto_relevant.model_name
                ) if auto_relevant is not None else None,
                suggested_record_type=auto_record_type,
                agency_suggestions=agency_suggestions,
                batch_info=await GetAnnotationBatchInfoQueryBuilder(
                    batch_id=self.batch_id,
                    models=[
                        UserUrlAgencySuggestion,
                    ]
                ).run(session),
                location_suggestions=location_suggestions,
                name_suggestions=name_suggestions
            )
        )