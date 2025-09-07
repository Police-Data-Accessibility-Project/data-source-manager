from sqlalchemy import CTE, select

from src.core.tasks.url.operators.agency_identification.subtasks.impl.homepage_match_.queries.ctes.whitelisted_root_urls import \
    WHITELISTED_ROOT_URLS_CTE
from src.db.models.impl.link.urls_root_url.sqlalchemy import LinkURLRootURL
from src.db.models.views.unvalidated_url import UnvalidatedURL

UNVALIDATED_URLS_WITH_ROOT: CTE = (
    select(
        UnvalidatedURL.url_id,
        LinkURLRootURL.root_url_id
    )
    .join(
        LinkURLRootURL,
        UnvalidatedURL.url_id == LinkURLRootURL.url_id
    )
    .join(
        WHITELISTED_ROOT_URLS_CTE,
        WHITELISTED_ROOT_URLS_CTE.c.id == LinkURLRootURL.root_url_id
    )
    .cte("unvalidated_urls_with_root")
)