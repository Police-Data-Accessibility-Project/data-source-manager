from typing import Sequence

from sqlalchemy import select, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.collectors.enums import CollectorType
from src.core.tasks.url.operators.agency_identification.subtasks.impl.ckan_.params import CKANAgencyIDSubtaskParams
from src.db.helpers.session import session_helper as sh
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.queries.base.builder import QueryBuilderBase


class GetCKANAgencyIDSubtaskParamsQueryBuilder(QueryBuilderBase):

    async def run(
        self,
        session: AsyncSession
    ) -> list[CKANAgencyIDSubtaskParams]:
        query = (
            select(
                URL.id,
                URL.collector_metadata
            )
            .join(
                LinkBatchURL,
                LinkBatchURL.url_id == URL.id,
            )
            .join(
                Batch,
                Batch.id == LinkBatchURL.batch_id,
            )
            .where(
                Batch.strategy.in_(
                    (
                        CollectorType.CKAN.value,
                    )
                ),
            )
            .limit(500)
        )

        results: Sequence[RowMapping] = await sh.mappings(session, query=query)
        return [
            CKANAgencyIDSubtaskParams(
                url_id=mapping["id"],
                collector_metadata=mapping["collector_metadata"],
            )
            for mapping in results
        ]
