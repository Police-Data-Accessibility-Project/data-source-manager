from sqlalchemy import select, or_, exists, func, text, CTE, ColumnElement

from src.db.helpers.query import not_exists_url
from src.db.models.impl.flag.checked_for_ia.sqlalchemy import FlagURLCheckedForInternetArchives
from src.db.models.impl.url.core.sqlalchemy import URL


class CheckURLInternetArchivesCTEContainer:

    def __init__(self):

        self._cte = (
            select(
                URL.id.label("url_id"),
                URL.url
            )
            .where(
                or_(
                    not_exists_url(FlagURLCheckedForInternetArchives),
                    exists(
                        select(FlagURLCheckedForInternetArchives.url_id)
                        .where(
                            FlagURLCheckedForInternetArchives.url_id == URL.id,
                            ~FlagURLCheckedForInternetArchives.success,
                            FlagURLCheckedForInternetArchives.created_at < func.now() - text("INTERVAL '1 week'")
                        )
                    )
                )
            ).cte("check_url_internet_archives_prereq")
        )

    @property
    def cte(self) -> CTE:
        return self._cte

    @property
    def url_id(self) -> ColumnElement[int]:
        return self._cte.c.url_id

    @property
    def url(self) -> ColumnElement[str]:
        return self._cte.c.url