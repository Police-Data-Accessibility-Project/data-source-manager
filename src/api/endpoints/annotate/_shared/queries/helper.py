"""
This module contains helper functions for the annotate GET queries
"""

from sqlalchemy import Select, case
from sqlalchemy.orm import joinedload

from src.db.models.impl.url.core.enums import URLSource
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.views.unvalidated_url import UnvalidatedURL
from src.db.models.views.url_anno_count import URLAnnotationCount
from src.db.models.views.url_annotations_flags import URLAnnotationFlagsView


def get_select() -> Select:
    return (
        Select(URL)
        # URL Must be unvalidated
        .join(
            UnvalidatedURL,
            UnvalidatedURL.url_id == URL.id
        )
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
    query = (
        # Add load options
        query.options(
            joinedload(URL.html_content),
            joinedload(URL.user_relevant_suggestions),
            joinedload(URL.user_record_type_suggestions),
            joinedload(URL.name_suggestions),
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