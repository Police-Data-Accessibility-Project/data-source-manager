from typing import Sequence

from sqlalchemy import select, exists

from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.subtask.container import \
    SubtaskCTEContainer
from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.subtask.helpers import \
    get_exists_subtask_query
from src.db.models.impl.flag.root_url.sqlalchemy import FlagRootURL
from src.db.models.impl.link.urls_root_url.sqlalchemy import LinkURLRootURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.suggestion.agency.subtask.enum import AutoAgencyIDSubtaskType
from src.db.models.views.meta_url import MetaURL

NOT_ROOT_URL_FLAG = (
    ~exists()
    .where(
        FlagRootURL.url_id == URL.id,
    )
)

NOT_META_URL_FLAG = (
    ~exists()
    .where(
        MetaURL.url_id == URL.id,
    )
)

BLACKLISTED_ROOTS: Sequence[str] = (
    'https://www.facebook.com',
    'https://www.countyoffice.org',
    '://',
    'https://www.usmarshals.gov',
    'https://www.mapquest.com',
    'https://catalog.data.gov',
    'https://www.muckrock.com'
)

# Root URL must not be blacklisted
WHITELISTED_ROOT_URL = (
    select(
        URL.id
    )
    .join(
        FlagRootURL,
        FlagRootURL.url_id == URL.id,
    )
    .where(
        URL.url.notin_(BLACKLISTED_ROOTS),
    )
    .cte("whitelisted_root_url")
)

ROOT_URLS_WITH_META_URLS = (
    select(
        WHITELISTED_ROOT_URL.c.id
    )
    .where(
        exists()
        .where(
            LinkURLRootURL.root_url_id == WHITELISTED_ROOT_URL.c.id,
            LinkURLRootURL.url_id == MetaURL.url_id,
        )
    )
    .cte("root_urls_with_meta_urls")
)

HAS_ROOT_URL_WITH_META_URLS = (
    exists()
    .where(
        LinkURLRootURL.root_url_id == ROOT_URLS_WITH_META_URLS.c.id,
        LinkURLRootURL.url_id == URL.id,
    )
)


cte = (
    select(
        URL.id,
        get_exists_subtask_query(
            AutoAgencyIDSubtaskType.HOMEPAGE_MATCH,
        )
    )
    .join(
        LinkURLRootURL,
        LinkURLRootURL.url_id == URL.id,
    )
    .where(
        NOT_META_URL_FLAG,
        NOT_ROOT_URL_FLAG,
        HAS_ROOT_URL_WITH_META_URLS,

    )
    .cte("homepage_eligible")
)

HOMEPAGE_SUBTASK_CONTAINER = SubtaskCTEContainer(
    cte,
)