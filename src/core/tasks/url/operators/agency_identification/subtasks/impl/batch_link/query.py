from typing import Sequence

from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.url.operators.agency_identification.subtasks.impl.batch_link.params import \
    AgencyBatchLinkSubtaskParams
from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.eligible import \
    EligibleContainer
from src.db.models.impl.link.agency_batch.sqlalchemy import LinkAgencyBatch
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.queries.base.builder import QueryBuilderBase
from src.db.helpers.session import session_helper as sh

class GetLocationBatchLinkSubtaskParamsQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> list[AgencyBatchLinkSubtaskParams]:
        container = EligibleContainer()
        query = (
            select(
                container.url_id,
                LinkAgencyBatch.agency_id,
            )
            .select_from(container.cte)
            .join(
                LinkBatchURL,
                LinkBatchURL.url_id == container.url_id,
            )
            .join(
                LinkAgencyBatch,
                LinkAgencyBatch.batch_id == LinkBatchURL.batch_id,
            )
            .where(
                container.batch_link,
            )
            .limit(500)
        )
        results: Sequence[RowMapping] = await sh.mappings(session, query=query)
        return [
            AgencyBatchLinkSubtaskParams(
                url_id=mapping["id"],
                agency_id=mapping["agency_id"],
            )
            for mapping in results
        ]