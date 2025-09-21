from sqlalchemy import CTE, select, and_, or_

from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.suggestion.agency.user import UserUrlAgencySuggestion
from src.db.models.impl.url.suggestion.location.user.sqlalchemy import UserLocationSuggestion
from src.db.models.impl.url.suggestion.record_type.user import UserRecordTypeSuggestion
from src.db.models.impl.url.suggestion.relevant.user import UserRelevantSuggestion


def build_cte(user_id: int) -> CTE:
    query = (
        select(
            URL.id
        )
    )
    for model in [
        UserLocationSuggestion,
        UserRelevantSuggestion,
        UserRecordTypeSuggestion,
        UserUrlAgencySuggestion
    ]:
        query = query.outerjoin(
            model,
            and_(
                model.url_id == URL.id,
                model.user_id == user_id
            )
        )
    query = query.where(
        and_(
            UserLocationSuggestion.user_id.is_(None),
            UserRelevantSuggestion.user_id.is_(None),
            UserRecordTypeSuggestion.user_id.is_(None),
            UserUrlAgencySuggestion.user_id.is_(None)
        )
    )
    return query.cte()
