from sqlalchemy import select, func, and_

from src.api.endpoints.contributions.user.queries.annotated_and_validated import AnnotatedAndValidatedCTEContainer
from src.api.endpoints.contributions.user.queries.templates.agreement import AgreementCTEContainer
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.url.suggestion.relevant.user import UserURLTypeSuggestion


def get_url_type_agreement_cte_container(
    inner_cte: AnnotatedAndValidatedCTEContainer
) -> AgreementCTEContainer:

    # Count CTE is number of User URL Type Suggestions
    count_cte = (
        select(
            inner_cte.user_id,
            func.count()
        )
        .join(
            UserURLTypeSuggestion,
            UserURLTypeSuggestion.url_id == inner_cte.url_id
        )
        .join(
            FlagURLValidated,
            FlagURLValidated.url_id == inner_cte.url_id
        )
        .group_by(
            inner_cte.user_id
        )
        .cte("url_type_count_total")
    )

    agreed_cte = (
        select(
            inner_cte.user_id,
            func.count()
        )
        .join(
            UserURLTypeSuggestion,
            UserURLTypeSuggestion.url_id == inner_cte.url_id
        )
        .join(
            FlagURLValidated,
            and_(
                FlagURLValidated.url_id == inner_cte.url_id,
                UserURLTypeSuggestion.type == FlagURLValidated.type

            )
        )
        .group_by(
            inner_cte.user_id
        )
        .cte("url_type_count_agreed")
    )

    return AgreementCTEContainer(
        count_cte=count_cte,
        agreed_cte=agreed_cte,
        name="url_type"
    )

