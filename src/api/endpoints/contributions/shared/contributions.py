from sqlalchemy import select, func, CTE, Column

from src.db.models.impl.annotation.url_type.user.sqlalchemy import AnnotationUserURLType


class ContributionsCTEContainer:

    def __init__(self):
        self._cte = (
            select(
                AnnotationUserURLType.user_id,
                func.count().label("count")
            )
            .group_by(
                AnnotationUserURLType.user_id
            )
            .cte("contributions")
        )

    @property
    def cte(self) -> CTE:
        return self._cte

    @property
    def count(self) -> Column[int]:
        return self.cte.c.count

    @property
    def user_id(self) -> Column[int]:
        return self.cte.c.user_id

