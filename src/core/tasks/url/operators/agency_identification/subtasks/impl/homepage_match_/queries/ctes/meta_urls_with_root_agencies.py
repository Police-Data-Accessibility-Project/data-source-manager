from sqlalchemy import CTE, select

from src.core.tasks.url.operators.agency_identification.subtasks.impl.homepage_match_.queries.ctes.meta_urls_with_root import \
    META_ROOT_URLS_CTE
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency

META_ROOT_URLS_WITH_AGENCIES: CTE = (
    select(
        META_ROOT_URLS_CTE.c.meta_url_id,
        META_ROOT_URLS_CTE.c.root_url_id,
        LinkURLAgency.agency_id
    )
    .join(
        LinkURLAgency,
        META_ROOT_URLS_CTE.c.meta_url_id == LinkURLAgency.url_id
    )
    .cte(
        "meta_root_urls_with_agencies"
    )
)