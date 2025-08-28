from sqlalchemy import Select, case, Label, and_, exists
from sqlalchemy.sql.functions import count, coalesce, func

from src.collectors.enums import URLStatus, CollectorType
from src.core.enums import BatchStatus
from src.db.models.impl.flag.url_validated.enums import URLValidatedType
from src.db.models.impl.flag.url_validated.sqlalchemy import FlagURLValidated
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.url.data_source.sqlalchemy import URLDataSource
from src.db.queries.base.builder import QueryBuilderBase
from src.db.queries.helpers import add_page_offset
from src.db.queries.implementations.core.get.recent_batch_summaries.url_counts.cte.all import ALL_CTE
from src.db.queries.implementations.core.get.recent_batch_summaries.url_counts.cte.duplicate import DUPLICATE_CTE
from src.db.queries.implementations.core.get.recent_batch_summaries.url_counts.cte.error import ERROR_CTE
from src.db.queries.implementations.core.get.recent_batch_summaries.url_counts.cte.not_relevant import NOT_RELEVANT_CTE
from src.db.queries.implementations.core.get.recent_batch_summaries.url_counts.cte.pending import PENDING_CTE
from src.db.queries.implementations.core.get.recent_batch_summaries.url_counts.cte.submitted import SUBMITTED_CTE
from src.db.queries.implementations.core.get.recent_batch_summaries.url_counts.labels import URLCountsLabels


class URLCountsCTEQueryBuilder(QueryBuilderBase):

    def __init__(
        self,
        page: int = 1,
        collector_type: CollectorType | None = None,
        status: BatchStatus | None = None,
        batch_id: int | None = None
    ):
        super().__init__(URLCountsLabels())
        self.page = page
        self.collector_type = collector_type
        self.status = status
        self.batch_id = batch_id


    def get_core_query(self):
        labels: URLCountsLabels = self.labels
        query = (
            Select(
                Batch.id.label(labels.batch_id),
                func.coalesce(DUPLICATE_CTE.count, 0).label(labels.duplicate),
                func.coalesce(SUBMITTED_CTE.count, 0).label(labels.submitted),
                func.coalesce(PENDING_CTE.count, 0).label(labels.pending),
                func.coalesce(ALL_CTE.count, 0).label(labels.total),
                func.coalesce(NOT_RELEVANT_CTE.count, 0).label(labels.not_relevant),
                func.coalesce(ERROR_CTE.count, 0).label(labels.error),
            )
            .select_from(Batch)
        )
        for cte in [DUPLICATE_CTE, SUBMITTED_CTE, PENDING_CTE, ALL_CTE, NOT_RELEVANT_CTE, ERROR_CTE]:
            query = query.outerjoin(
                cte.cte,
                Batch.id == cte.batch_id
            )
        return query


    def build(self):
        query = self.get_core_query()
        query = self.apply_collector_type_filter(query)
        query = self.apply_status_filter(query)
        query = self.apply_batch_id_filter(query)
        query = add_page_offset(query, page=self.page)
        query = query.order_by(Batch.id)
        self.query = query.cte("url_counts")

    def apply_batch_id_filter(self, query: Select):
        if self.batch_id is None:
            return query
        return query.where(Batch.id == self.batch_id)

    def apply_collector_type_filter(self, query: Select):
        if self.collector_type is None:
            return query
        return query.where(Batch.strategy == self.collector_type.value)

    def apply_status_filter(self, query: Select):
        if self.status is None:
            return query
        return query.where(Batch.status == self.status.value)
