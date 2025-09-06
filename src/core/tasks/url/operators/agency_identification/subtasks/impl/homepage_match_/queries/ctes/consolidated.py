from sqlalchemy import CTE, select

from src.core.tasks.url.operators.agency_identification.subtasks.impl.homepage_match_.queries.ctes.count_agency_per_url import \
    COUNT_AGENCY_PER_URL_CTE
from src.core.tasks.url.operators.agency_identification.subtasks.impl.homepage_match_.queries.ctes.unvalidated_urls_with_root import \
    UNVALIDATED_URLS_WITH_ROOT
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency

CONSOLIDATED_CTE: CTE = (
    select(
        UNVALIDATED_URLS_WITH_ROOT.c.url_id,
        LinkURLAgency.agency_id,
        COUNT_AGENCY_PER_URL_CTE.c.agency_count,
    )
    .join(
        COUNT_AGENCY_PER_URL_CTE,
        COUNT_AGENCY_PER_URL_CTE.c.url_id == UNVALIDATED_URLS_WITH_ROOT.c.url_id
    )
    .join(
        LinkURLAgency,
        LinkURLAgency.url_id == UNVALIDATED_URLS_WITH_ROOT.c.url_id
    )
    .where(
        COUNT_AGENCY_PER_URL_CTE.c.agency_count >= 1
    )
    .cte("consolidated")
)