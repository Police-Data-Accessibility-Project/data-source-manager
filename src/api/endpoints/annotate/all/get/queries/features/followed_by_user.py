from sqlalchemy import exists, select, literal, Exists

from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.link.location__user_follow import LinkLocationUserFollow
from src.db.models.impl.link.location_batch.sqlalchemy import LinkLocationBatch
from src.db.models.impl.url.core.sqlalchemy import URL


def get_followed_by_user_feature(
    user_id: int
) -> Exists:
    query = (
        exists(
            select(literal(1))
            .select_from(LinkBatchURL)
            .join(
                LinkLocationBatch,
                LinkLocationBatch.batch_id == LinkBatchURL.batch_id
            )
            .join(
                LinkLocationUserFollow,
                LinkLocationUserFollow.location_id == LinkLocationBatch.location_id
            )
            .where(
                URL.id == LinkBatchURL.url_id,
                LinkLocationUserFollow.user_id == user_id
            )
        ).label("followed_by_user")
    )
    return query