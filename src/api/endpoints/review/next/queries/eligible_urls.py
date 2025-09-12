from sqlalchemy import CTE, select, Select

from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.views.url_annotations_flags import URLAnnotationFlagsView

uafw = URLAnnotationFlagsView

def build_eligible_urls_cte(batch_id: int | None = None) -> CTE:
    query: Select = (
        select(
            uafw.url_id,
        )
        .where(
            # uafw.has_auto_agency_suggestion.is_(True),
            # uafw.has_auto_record_type_suggestion.is_(True),
            # uafw.has_auto_relevant_suggestion.is_(True),
            uafw.has_user_relevant_suggestion.is_(True),
            uafw.has_user_agency_suggestion.is_(True),
            uafw.has_user_record_type_suggestion.is_(True),
            uafw.was_reviewed.is_(False)
        )
    )

    if batch_id is not None:
        query = (
            query.join(
                LinkBatchURL,
                LinkBatchURL.url_id == uafw.url_id
            )
            .where(
                LinkBatchURL.batch_id == batch_id
            )
        )

    return query.cte("eligible_urls")
