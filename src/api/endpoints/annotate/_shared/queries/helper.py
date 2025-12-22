"""
This module contains helper functions for the annotate GET queries
"""

from sqlalchemy import Select, case, exists, select
from sqlalchemy.orm import joinedload

from src.collectors.enums import URLStatus
from src.db.helpers.query import exists_url, not_exists_url
from src.db.models.impl.flag.url_suspended.sqlalchemy import FlagURLSuspended
from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.views.unvalidated_url import UnvalidatedURL
from src.db.models.views.url_anno_count import URLAnnotationCount
from src.db.models.views.url_annotations_flags import URLAnnotationFlagsView


def get_select() -> Select:
    return (
        Select(URL)

        .join(
            URLAnnotationFlagsView,
            URLAnnotationFlagsView.url_id == URL.id
        )
        .join(
            URLAnnotationCount,
            URLAnnotationCount.url_id == URL.id
        )
    )

def conclude(query: Select) -> Select:
    # Add common where conditions
    query = query.where(
        URL.status == URLStatus.OK.value,
        not_exists_url(
            FlagURLSuspended
        ),
        # URL Must be unvalidated
        exists_url(
            UnvalidatedURL
        )
    )


    query = (
        # Add load options
        query.options(
            joinedload(URL.html_content),
            joinedload(URL.user_url_type_suggestions),
            joinedload(URL.user_record_type_suggestions),
            joinedload(URL.anon_record_type_suggestions),
            joinedload(URL.anon_url_type_suggestions),
        )
        # Sorting Priority
        .order_by(
            # Privilege manually submitted URLs first
            case(
                (URL.source == URLSource.MANUAL, 0),
                else_=1
            ).asc(),
            # Break ties by favoring URL with higher total annotations
            URLAnnotationCount.total_anno_count.desc(),
            # Break additional ties by favoring least recently created URLs
            URL.id.asc()
        )
        # Limit to 1 result
        .limit(1)
    )
    return query