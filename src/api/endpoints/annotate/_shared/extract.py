from sqlalchemy.ext.asyncio import AsyncSession

from src.api.endpoints.annotate._shared.queries.get_annotation_batch_info import GetAnnotationBatchInfoQueryBuilder
from src.api.endpoints.annotate.all.get.models.agency import AgencyAnnotationResponseOuterInfo
from src.api.endpoints.annotate.all.get.models.location import LocationAnnotationResponseOuterInfo
from src.api.endpoints.annotate.all.get.models.name import NameAnnotationSuggestion
from src.api.endpoints.annotate.all.get.models.record_type import RecordTypeAnnotationSuggestion
from src.api.endpoints.annotate.all.get.models.response import GetNextURLForAllAnnotationResponse, \
    GetNextURLForAllAnnotationInnerResponse
from src.api.endpoints.annotate.all.get.models.url_type import URLTypeAnnotationSuggestion
from src.api.endpoints.annotate.all.get.queries.agency.core import GetAgencySuggestionsQueryBuilder
from src.api.endpoints.annotate.all.get.queries.convert import \
    convert_user_url_type_suggestion_to_url_type_annotation_suggestion, \
    convert_user_record_type_suggestion_to_record_type_annotation_suggestion
from src.api.endpoints.annotate.all.get.queries.location_.core import GetLocationSuggestionsQueryBuilder
from src.api.endpoints.annotate.all.get.queries.name.core import GetNameSuggestionsQueryBuilder
from src.db.dto_converter import DTOConverter
from src.db.dtos.url.mapping import URLMapping
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.suggestion.agency.user import UserUrlAgencySuggestion


async def extract_and_format_get_annotation_result(
    session: AsyncSession,
    url: URL,
    batch_id: int | None = None
):
    html_response_info = DTOConverter.html_content_list_to_html_response_info(
        url.html_content
    )
    url_type_suggestions: list[URLTypeAnnotationSuggestion] = \
        convert_user_url_type_suggestion_to_url_type_annotation_suggestion(
            url.user_relevant_suggestions
        )
    record_type_suggestions: list[RecordTypeAnnotationSuggestion] = \
        convert_user_record_type_suggestion_to_record_type_annotation_suggestion(
            url.user_record_type_suggestions
        )
    agency_suggestions: AgencyAnnotationResponseOuterInfo = \
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
            url_type_suggestions=url_type_suggestions,
            record_type_suggestions=record_type_suggestions,
            agency_suggestions=agency_suggestions,
            batch_info=await GetAnnotationBatchInfoQueryBuilder(
                batch_id=batch_id,
                models=[
                    UserUrlAgencySuggestion,
                ]
            ).run(session),
            location_suggestions=location_suggestions,
            name_suggestions=name_suggestions
        )
    )
