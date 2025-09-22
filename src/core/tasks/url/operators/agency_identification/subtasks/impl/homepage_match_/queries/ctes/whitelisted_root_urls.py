from sqlalchemy import CTE, select, func

from src.db.models.impl.flag.root_url.sqlalchemy import FlagRootURL
from src.db.models.impl.flag.url_validated.enums import URLType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.impl.link.urls_root_url.sqlalchemy import LinkURLRootURL
from src.db.models.impl.url.core.sqlalchemy import URL

WHITELISTED_ROOT_URLS_CTE: CTE = (
    select(
        URL.id
    )
    .join(
        FlagRootURL,
        URL.id == FlagRootURL.url_id
    )
    # Must be linked to other URLs
    .join(
        LinkURLRootURL,
        URL.id == LinkURLRootURL.root_url_id
    )
    # Those URLs must be meta URLS
    .join(
        FlagURLValidated,
        FlagURLValidated.url_id == LinkURLRootURL.url_id
    )
    # Get the Agency URLs for those URLs
    .join(
        LinkURLAgency,
        LinkURLAgency.url_id == LinkURLRootURL.url_id
    )
    .where(
        # The connected URLs must be Meta URLs
        FlagURLValidated.type == URLType.META_URL,
        # Root URL can't be "https://catalog.data.gov"
        URL.url != "https://catalog.data.gov"
    )
    .group_by(
        URL.id
    )
    # Must have no more than two agencies connected
    .having(
        func.count(LinkURLAgency.agency_id) <= 2
    )
    .cte("whitelisted_root_urls")
)