from typing import Sequence

from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.collectors.enums import CollectorType
from src.core.tasks.url.operators.agency_identification.subtasks.impl.muckrock_.params import \
    MuckrockAgencyIDSubtaskParams
from src.core.tasks.url.operators.agency_identification.subtasks.queries.survey.queries.ctes.eligible import \
    EligibleContainer
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase


class GetMuckrockAgencyIDSubtaskParamsQueryBuilder(QueryBuilderBase):

    async def run(
        self,
        session: AsyncSession
    ) -> list[MuckrockAgencyIDSubtaskParams]:
        container = EligibleContainer()

        query = (
            select(
                container.url_id,
                URL.collector_metadata
            )
            .join(
                URL,
                URL.id == container.url_id,
            )
            .where(
                container.muckrock,
            )
            .limit(500)
        )

        results: Sequence[RowMapping] = await sh.mappings(session, query=query)
        return [
            MuckrockAgencyIDSubtaskParams(
                url_id=mapping["id"],
                collector_metadata=mapping["collector_metadata"],
            )
            for mapping in results
        ]

