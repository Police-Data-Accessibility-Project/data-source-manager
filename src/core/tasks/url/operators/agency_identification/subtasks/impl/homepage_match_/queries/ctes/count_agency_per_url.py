from sqlalchemy import CTE, func, select

from src.core.tasks.url.operators.agency_identification.subtasks.impl.homepage_match_.queries.ctes.meta_urls_with_root import \
    META_ROOT_URLS_CTE
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency

COUNT_AGENCY_PER_URL_CTE: CTE = (
    select(
        META_ROOT_URLS_CTE.c.root_url_id,
        func.count(LinkURLAgency.agency_id).label("agency_count")
    )
    .join(
        LinkURLAgency,
        META_ROOT_URLS_CTE.c.meta_url_id == LinkURLAgency.url_id
    )
    .group_by(
        META_ROOT_URLS_CTE.c.root_url_id
    )
    .cte("count_agency_per_url")
)