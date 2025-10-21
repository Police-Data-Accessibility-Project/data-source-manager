from http import HTTPStatus
from typing import Any

from sqlalchemy import Select, select, exists, func, Subquery, and_, not_, ColumnElement
from sqlalchemy.orm import selectinload

from src.collectors.enums import URLStatus
from src.db.enums import TaskType
from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.link.task_url import LinkTaskURL
from src.db.models.impl.task.core import Task
from src.db.models.impl.task.enums import TaskStatus
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.optional_ds_metadata.sqlalchemy import URLOptionalDataSourceMetadata
from src.db.models.impl.url.scrape_info.sqlalchemy import URLScrapeInfo
from src.db.models.impl.url.web_metadata.sqlalchemy import URLWebMetadata
from src.db.types import UserSuggestionType


class StatementComposer:
    """
    Assists in the composition of SQLAlchemy statements
    """

    @staticmethod
    def has_non_errored_urls_without_html_data() -> Select:
        exclude_subquery = (
            select(1).
            select_from(LinkTaskURL).
            join(Task, LinkTaskURL.task_id == Task.id).
            where(LinkTaskURL.url_id == URL.id).
            where(Task.task_type == TaskType.HTML.value).
            where(Task.task_status == TaskStatus.COMPLETE.value)
         )
        query = (
            select(URL)
            .join(URLWebMetadata)
            .outerjoin(URLScrapeInfo)
            .where(
                URLScrapeInfo.id == None,
                ~exists(exclude_subquery),
                URLWebMetadata.status_code == HTTPStatus.OK.value,
                URLWebMetadata.content_type.like("%html%"),
            )
            .options(
                selectinload(URL.batch)
            )
        )
        return query

    @staticmethod
    def exclude_urls_with_extant_model(
        statement: Select,
        model: Any
    ):
        return (statement.where(
                        ~exists(
                            select(model.id).
                            where(
                                model.url_id == URL.id
                            )
                        )
                    ))

    @staticmethod
    def simple_count_subquery(model, attribute: str, label: str) -> Subquery:
        attr_value = getattr(model, attribute)
        return select(
            attr_value,
            func.count(attr_value).label(label)
        ).group_by(attr_value).subquery()

    @staticmethod
    def pending_urls_missing_miscellaneous_metadata_query() -> Select:
        query = select(URL).where(
            and_(
                URL.status == URLStatus.OK.value,
                URL.name == None,
                URL.description == None,
                URLOptionalDataSourceMetadata.url_id == None
                )
            ).outerjoin(
                URLOptionalDataSourceMetadata
            ).join(
                LinkBatchURL
            ).join(
                Batch
            )

        return query

    @staticmethod
    def user_suggestion_exists(
        model_to_include: UserSuggestionType
    ) -> ColumnElement[bool]:
        subquery = exists(
            select(model_to_include)
            .where(
                model_to_include.url_id == URL.id,
            )
        )
        return subquery

    @staticmethod
    def user_suggestion_not_exists(
            model_to_exclude: UserSuggestionType
    ) -> ColumnElement[bool]:
        subquery = not_(
            StatementComposer.user_suggestion_exists(model_to_exclude)
        )
        return subquery

    @staticmethod
    def count_distinct(field, label):
        return func.count(func.distinct(field)).label(label)
