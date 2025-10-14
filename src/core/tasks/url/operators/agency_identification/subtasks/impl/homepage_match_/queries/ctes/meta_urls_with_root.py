from sqlalchemy import CTE, select

from src.core.tasks.url.operators.agency_identification.subtasks.impl.homepage_match_.queries.ctes.whitelisted_root_urls import \
    WHITELISTED_ROOT_URLS_CTE
from src.db.models.impl.link.urls_root_url.sqlalchemy import LinkURLRootURL
from src.db.models.views.meta_url import MetaURL

META_ROOT_URLS_CTE: CTE = (
    select(
        MetaURL.url_id.label("meta_url_id"),
        LinkURLRootURL.root_url_id
    )
    .join(
        LinkURLRootURL,
        MetaURL.url_id == LinkURLRootURL.url_id
    )
    # Must be a Whitelisted Root URL
    .join(
        WHITELISTED_ROOT_URLS_CTE,
        WHITELISTED_ROOT_URLS_CTE.c.id == LinkURLRootURL.root_url_id
    )
    .cte("meta_root_urls")
)