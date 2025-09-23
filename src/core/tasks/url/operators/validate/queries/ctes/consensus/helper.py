from sqlalchemy import Select, CTE, select

from src.core.tasks.url.operators.validate.queries.ctes.scored import ScoredCTEContainer


def build_validation_query(
    scored_cte: ScoredCTEContainer,
    label: str
) -> CTE:
        return select(
            scored_cte.url_id,
            scored_cte.entity.label(label)
        ).where(
            scored_cte.rnk == 1,
            scored_cte.max_votes >= 2,
            scored_cte.votes == scored_cte.max_votes,
            scored_cte.num_labels_with_that_vote == 1
        ).cte(f"{label}_validation")
