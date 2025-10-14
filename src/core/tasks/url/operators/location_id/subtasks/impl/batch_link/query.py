from typing import Sequence

from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.location_id.subtasks.impl.batch_link.inputs import LocationBatchLinkInput
from src.core.tasks.url.operators.location_id.subtasks.impl.nlp_location_freq.constants import \
    NUMBER_OF_ENTRIES_PER_ITERATION
from src.core.tasks.url.operators.location_id.subtasks.queries.survey.queries.ctes.eligible import EligibleContainer
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.link.location_batch.sqlalchemy import LinkLocationBatch
from src.db.queries.base.builder import QueryBuilderBase
from src.db.helpers.session import session_helper as sh

class GetLocationBatchLinkQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[LocationBatchLinkInput]:
        container = EligibleContainer()
        query = (
            select(
                LinkLocationBatch.location_id,
                LinkBatchURL.url_id
            )
            .join(
                LinkLocationBatch,
                LinkBatchURL.batch_id == LinkLocationBatch.batch_id,
            )
            .join(
                container.cte,
                LinkBatchURL.url_id == container.url_id,
            )
            .where(
                container.batch_link,
            )
            .limit(NUMBER_OF_ENTRIES_PER_ITERATION)
        )

        mappings: Sequence[RowMapping] = await sh.mappings(session, query=query)
        inputs: list[LocationBatchLinkInput] = [
            LocationBatchLinkInput(
                location_id=mapping["location_id"],
                url_id=mapping["url_id"],
            )
            for mapping in mappings
        ]
        return inputs
