from collections import Counter

from src.api.endpoints.annotate.agency.get.dto import GetNextURLForAgencyAgencyInfo
from src.api.endpoints.annotate.relevance.get.dto import RelevanceAnnotationResponseInfo
from src.api.endpoints.review.next.dto import FinalReviewAnnotationRelevantInfo, FinalReviewAnnotationRecordTypeInfo, \
    FinalReviewAnnotationAgencyInfo
from src.core.enums import RecordType, SuggestionType
from src.core.tasks.url.operators.html.scraper.parser.dtos.response_html import ResponseHTMLInfo
from src.core.tasks.url.operators.html.scraper.parser.mapping import ENUM_TO_ATTRIBUTE_MAPPING
from src.db.dtos.url.html_content import URLHTMLContentInfo
from src.db.dtos.url.with_html import URLWithHTML
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.html.content.enums import HTMLContentType
from src.db.models.impl.url.html.content.sqlalchemy import URLHTMLContent
from src.db.models.impl.url.suggestion.agency.user import UserUrlAgencySuggestion
from src.db.models.impl.url.suggestion.record_type.auto import AutoRecordTypeSuggestion
from src.db.models.impl.url.suggestion.record_type.user import UserRecordTypeSuggestion
from src.db.models.impl.url.suggestion.relevant.auto.sqlalchemy import AutoRelevantSuggestion
from src.db.models.impl.url.suggestion.relevant.user import UserURLTypeSuggestion


class DTOConverter:

    """
    Converts SQLAlchemy objects to dtos
    """

    @staticmethod
    def final_review_annotation_relevant_info(
        user_suggestions: list[UserURLTypeSuggestion],
        auto_suggestion: AutoRelevantSuggestion
    ) -> FinalReviewAnnotationRelevantInfo:

        auto_value = RelevanceAnnotationResponseInfo(
            is_relevant=auto_suggestion.relevant,
            confidence=auto_suggestion.confidence,
            model_name=auto_suggestion.model_name

        ) if auto_suggestion else None

        user_types = [suggestion.type for suggestion in user_suggestions]
        counter = Counter(user_types)
        return FinalReviewAnnotationRelevantInfo(
            auto=auto_value,
            user=dict(counter)
        )

    @staticmethod
    def final_review_annotation_record_type_info(
        user_suggestions: list[UserRecordTypeSuggestion],
        auto_suggestion: AutoRecordTypeSuggestion
    ):

        if auto_suggestion is None:
            auto_value = None
        else:
            auto_value = RecordType(auto_suggestion.record_type)

        record_types: list[RecordType] = [suggestion.record_type for suggestion in user_suggestions]
        counter = Counter(record_types)
        user_value = dict(counter)

        return FinalReviewAnnotationRecordTypeInfo(
            auto=auto_value,
            user=user_value
        )



    @staticmethod
    def url_list_to_url_with_html_list(url_list: list[URL]) -> list[URLWithHTML]:
        return [DTOConverter.url_to_url_with_html(url) for url in url_list]

    @staticmethod
    def url_to_url_with_html(url: URL) -> URLWithHTML:
        url_val = url.url
        url_id = url.id
        html_infos = []
        for html_info in url.html_content:
            html_infos.append(
                URLHTMLContentInfo(
                    **html_info.__dict__
                )
            )

        return URLWithHTML(
            url=url_val,
            url_id=url_id,
            html_infos=html_infos
        )

    @staticmethod
    def html_content_list_to_html_response_info(html_content_list: list[URLHTMLContent]):
        response_html_info = ResponseHTMLInfo()

        for html_content in html_content_list:
            content_type = HTMLContentType(html_content.content_type)
            content = html_content.content

            setattr(
                response_html_info,
                ENUM_TO_ATTRIBUTE_MAPPING[content_type],
                content
            )


        return response_html_info


