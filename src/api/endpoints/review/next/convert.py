from src.api.endpoints.annotate.agency.get.dto import GetNextURLForAgencyAgencyInfo
from src.api.endpoints.review.next.dto import FinalReviewAnnotationAgencyInfo, FinalReviewAnnotationAgencyAutoInfo
from src.core.enums import SuggestionType
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.impl.url.suggestion.agency.subtask.sqlalchemy import URLAutoAgencyIDSubtask
from src.db.models.impl.url.suggestion.agency.user import UserUrlAgencySuggestion


def convert_agency_info_to_final_review_annotation_agency_info(
    subtasks: list[URLAutoAgencyIDSubtask],
    confirmed_agencies: list[LinkURLAgency],
    user_agency_suggestion: UserUrlAgencySuggestion
) -> FinalReviewAnnotationAgencyInfo:

    confirmed_agency_info: list[GetNextURLForAgencyAgencyInfo] = (
        _convert_confirmed_agencies_to_final_review_annotation_agency_info(
            confirmed_agencies
        )
    )

    agency_auto_info: FinalReviewAnnotationAgencyAutoInfo = (
        _convert_url_auto_agency_suggestions_to_final_review_annotation_agency_auto_info(
            subtasks
        )
    )

    agency_user_info: GetNextURLForAgencyAgencyInfo | None = (
        _convert_user_url_agency_suggestion_to_final_review_annotation_agency_user_info(
            user_agency_suggestion
        )
    )

    return FinalReviewAnnotationAgencyInfo(
        confirmed=confirmed_agency_info,
        user=agency_user_info,
        auto=agency_auto_info
    )

def _convert_confirmed_agencies_to_final_review_annotation_agency_info(
    confirmed_agencies: list[LinkURLAgency]
) -> list[GetNextURLForAgencyAgencyInfo]:
    results: list[GetNextURLForAgencyAgencyInfo] = []
    for confirmed_agency in confirmed_agencies:
        agency = confirmed_agency.agency
        agency_info = _convert_agency_to_get_next_url_for_agency_agency_info(
            suggestion_type=SuggestionType.CONFIRMED,
            agency=agency
        )
        results.append(agency_info)
    return results

def _convert_user_url_agency_suggestion_to_final_review_annotation_agency_user_info(
    user_url_agency_suggestion: UserUrlAgencySuggestion
) -> GetNextURLForAgencyAgencyInfo | None:
    suggestion = user_url_agency_suggestion
    if suggestion is None:
        return None
    if suggestion.is_new:
        return GetNextURLForAgencyAgencyInfo(
            suggestion_type=SuggestionType.NEW_AGENCY,
        )
    return _convert_agency_to_get_next_url_for_agency_agency_info(
        suggestion_type=SuggestionType.USER_SUGGESTION,
        agency=suggestion.agency
    )

def _convert_agency_to_get_next_url_for_agency_agency_info(
    suggestion_type: SuggestionType,
    agency: Agency
) -> GetNextURLForAgencyAgencyInfo:
    return GetNextURLForAgencyAgencyInfo(
        suggestion_type=suggestion_type,
        pdap_agency_id=agency.agency_id,
        agency_name=agency.name,
        state=agency.state,
        county=agency.county,
        locality=agency.locality
    )

def _convert_url_auto_agency_suggestions_to_final_review_annotation_agency_auto_info(
    subtasks: list[URLAutoAgencyIDSubtask]
) -> FinalReviewAnnotationAgencyAutoInfo:
    results: list[GetNextURLForAgencyAgencyInfo] = []
    count_agencies_not_found: int = 0
    for subtask in subtasks:
        if not subtask.agencies_found:
            count_agencies_not_found += 1
            continue
        for suggestion in subtask.suggestions:
            info: GetNextURLForAgencyAgencyInfo = _convert_agency_to_get_next_url_for_agency_agency_info(
                suggestion_type=SuggestionType.AUTO_SUGGESTION,
                agency=suggestion.agency
            )
            results.append(info)
    return FinalReviewAnnotationAgencyAutoInfo(
        unknown=count_agencies_not_found == len(subtasks),
        suggestions=results
    )
