from sqlalchemy import ColumnElement, exists, select, Select

from src.db.enums import TaskType
from src.db.models.impl import LinkBatchURL
from src.db.models.impl.link.task_url import LinkTaskURL
from src.db.models.impl.task.core import Task
from src.db.models.impl.task.enums import TaskStatus
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.scrape_info.sqlalchemy import URLScrapeInfo
from src.db.models.impl.url.web_metadata.sqlalchemy import URLWebMetadata
from src.db.models.materialized_views.url_status.sqlalchemy import URLStatusMaterializedView


def _exclude_completed_html_task_subquery() -> ColumnElement[bool]:
        return ~exists(
            select(1)
            .select_from(
                LinkTaskURL
            )
            .join(
                Task,
                LinkTaskURL.task_id == Task.id
            )
            .where(
                LinkTaskURL.url_id == URL.id,
                Task.task_type == TaskType.HTML.value,
                Task.task_status == TaskStatus.COMPLETE.value
            )
        )

def has_non_errored_urls_without_html_data() -> Select:
    query = (
        select(
            URL.id,
            URL.full_url,
        )
        .join(
            URLWebMetadata,
            URLWebMetadata.url_id == URL.id
        )
        .outerjoin(
            URLScrapeInfo
        )
        .where(
            URLScrapeInfo.url_id == None,
            _exclude_completed_html_task_subquery,
            URLWebMetadata.status_code == 200,
            URLWebMetadata.content_type.like("%html%"),
        )
    )
    return query
