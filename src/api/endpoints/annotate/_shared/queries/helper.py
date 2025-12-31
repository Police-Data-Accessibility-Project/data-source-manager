"""
This module contains helper functions for the annotate GET queries
"""

from sqlalchemy import Select, case, CTE, ColumnElement
from sqlalchemy.orm import joinedload

from src.collectors.enums import URLStatus
from src.db.helpers.query import exists_url, not_exists_url
from src.db.models.impl.flag.url_suspended.sqlalchemy import FlagURLSuspended
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.views.unvalidated_url import UnvalidatedURL
from src.db.models.views.url_anno_count import URLAnnotationCount
from src.db.models.views.url_annotations_flags import URLAnnotationFlagsView


def add_joins(query: Select) -> Select:
    query = (
        query
        .join(
            URLAnnotationFlagsView,
            URLAnnotationFlagsView.url_id == URL.id
        )
        .join(
            URLAnnotationCount,
            URLAnnotationCount.url_id == URL.id
        )
    )
    return query

def add_common_where_conditions(
    query: Select,
) -> Select:
    return query.where(
        not_exists_url(
            FlagURLSuspended
        ),
        # URL Must be unvalidated
        exists_url(
            UnvalidatedURL
        )
    )

def add_load_options(
    query: Select
) -> Select:
    return query.options(
        joinedload(URL.html_content),
        joinedload(URL.user_url_type_suggestions),
        joinedload(URL.user_record_type_suggestions),
        joinedload(URL.anon_record_type_suggestions),
        joinedload(URL.anon_url_type_suggestions),
    )

def bool_sort(
    condition: ColumnElement[bool]
) -> ColumnElement[int]:
    return case(
        (condition, 0),
        else_=1
    ).asc()

def common_sorts(
    base_cte: CTE
) -> list[ColumnElement[int]]:
    return [
        # Privilege URLs whose batches are associated with locations
          # followed by ANY user
        bool_sort(base_cte.c.followed_by_any_user),
        # Privilege Manually Submitted URLs
        bool_sort(URL.source == URLSource.MANUAL),
        # Privilege based on total number of user annotations
        URLAnnotationCount.user_url_type_count.desc(),
        # Privilege based on total number of anon annotations
        URLAnnotationCount.anon_url_type_count.desc(),
        # Privilege based on total number of auto annotations
        URLAnnotationCount.auto_url_type_count.desc(),
        # Break additional ties by favoring least recently created URLs
        URL.id.asc()
    ]

