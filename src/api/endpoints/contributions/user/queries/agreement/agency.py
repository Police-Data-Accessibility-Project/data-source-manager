from sqlalchemy import select, func, exists, and_, or_, any_, cast, Float

from src.api.endpoints.contributions.user.queries.templates.agreement import AgreementCTEContainer
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.impl.url.suggestion.agency.user import UserURLAgencySuggestion


def get_agency_agreement_cte_container() -> AgreementCTEContainer:

    uuas = UserURLAgencySuggestion
    fuv = FlagURLValidated
    lau = LinkURLAgency
    # CTE 1: All validated Meta URLs/Data Sources and their agencies
    validated_urls_with_agencies = (
        select(
            uuas.url_id,
            func.array_agg(lau.agency_id).label("agency_ids"),
        )
        .join(fuv, fuv.url_id == uuas.url_id)
        .join(lau, lau.url_id == uuas.url_id, isouter=True)
        .where(
            or_(
                uuas.is_new.is_(None),
                uuas.is_new.is_(False)
            ),
            or_(
                fuv.type == "meta url",
                fuv.type == "data source"
            ),
        )
        .group_by(uuas.url_id)
        .cte("validated_urls_with_agencies")
    )

    # CTE 2
    cte_2 = (
        select(
            validated_urls_with_agencies.c.url_id,
            validated_urls_with_agencies.c.agency_ids,
            uuas.is_new,
            uuas.user_id,
            uuas.agency_id.label("suggested_agency_id"),
            (uuas.agency_id == any_(validated_urls_with_agencies.c.agency_ids)).label(
                "is_suggested_agency_validated"
            ),
        )
        .join(
            validated_urls_with_agencies,
            validated_urls_with_agencies.c.url_id == uuas.url_id,
        )
        .cte("final")
    )

    count_cte = (
        select(
            cte_2.c.user_id,
            func.count()
        )
        .group_by(
            cte_2.c.user_id
        )
        .cte("count_cte")
    )

    agreed_cte = (
        select(
            cte_2.c.user_id,
            func.count()
        )
        .where(
            cte_2.c.is_suggested_agency_validated.is_(True)
        )
        .group_by(
            cte_2.c.user_id
        )
        .cte("agreed_cte")
    )

    return AgreementCTEContainer(
        count_cte=count_cte,
        agreed_cte=agreed_cte,
        name="agency"
    )
