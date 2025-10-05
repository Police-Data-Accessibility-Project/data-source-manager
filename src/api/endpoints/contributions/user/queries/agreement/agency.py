from sqlalchemy import select, func, exists

from src.api.endpoints.contributions.user.queries.annotated_and_validated import AnnotatedAndValidatedCTEContainer
from src.api.endpoints.contributions.user.queries.templates.agreement import AgreementCTEContainer
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.impl.url.suggestion.agency.user import UserUrlAgencySuggestion


def get_agency_agreement_cte_container(
    inner_cte: AnnotatedAndValidatedCTEContainer
) -> AgreementCTEContainer:

    count_cte = (
        select(
            inner_cte.user_id,
            func.count()
        )
        .join(
            UserUrlAgencySuggestion,
            inner_cte.user_id == UserUrlAgencySuggestion.user_id
        )
        .group_by(
            inner_cte.user_id
        )
        .cte("agency_count_total")
    )

    agreed_cte = (
        select(
            inner_cte.user_id,
            func.count()
        )
        .join(
            UserUrlAgencySuggestion,
            inner_cte.user_id == UserUrlAgencySuggestion.user_id
        )
        .where(
            exists()
            .where(
                LinkURLAgency.url_id == UserUrlAgencySuggestion.url_id,
                LinkURLAgency.agency_id == UserUrlAgencySuggestion.agency_id
            )
        )
        .group_by(
            inner_cte.user_id
        )
        .cte("agency_count_agreed")
    )

    return AgreementCTEContainer(
        count_cte=count_cte,
        agreed_cte=agreed_cte,
        name="agency"
    )
