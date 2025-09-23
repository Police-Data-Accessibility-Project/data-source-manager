from sqlalchemy import CTE, select, func, Column

from src.core.tasks.url.operators.validate.queries.ctes.counts.core import ValidatedCountsCTEContainer


class ScoredCTEContainer:

    def __init__(
        self,
        counts_cte: ValidatedCountsCTEContainer
    ):
        self._cte: CTE = (
            select(
                counts_cte.url_id,
                counts_cte.entity,
                counts_cte.votes,
                func.max(counts_cte.votes).over(
                    partition_by=counts_cte.entity
                ).label("max_votes"),
                func.dense_rank().over(
                    partition_by=counts_cte.entity,
                    order_by=counts_cte.votes.desc()
                ).label("rnk"),
                func.count().over(
                    partition_by=(
                        counts_cte.entity,
                        counts_cte.votes
                    )
                ).label("num_labels_with_that_vote")
            )
            .cte(f"scored_{counts_cte.cte.name}")
        )

    @property
    def cte(self) -> CTE:
        return self._cte

    @property
    def url_id(self) -> Column[int]:
        return self._cte.c.url_id

    @property
    def entity(self) -> Column:
        return self._cte.c.entity

    @property
    def votes(self) -> Column[int]:
        return self._cte.c.votes

    @property
    def max_votes(self) -> Column[int]:
        return self._cte.c.max_votes

    @property
    def rnk(self) -> Column[int]:
        return self._cte.c.rnk

    @property
    def num_labels_with_that_vote(self) -> Column[int]:
        return self._cte.c.num_labels_with_that_vote