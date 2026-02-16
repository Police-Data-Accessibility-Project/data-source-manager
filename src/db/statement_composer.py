from sqlalchemy import Select, select, exists, func, Subquery, not_, ColumnElement

from src.db.models.impl.batch.sqlalchemy import Batch
from src.db.models.impl.link.batch_url.sqlalchemy import LinkBatchURL
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.optional_ds_metadata.sqlalchemy import URLOptionalDataSourceMetadata
from src.db.types import UserSuggestionType


class StatementComposer:
    """
    Assists in the composition of SQLAlchemy statements
    """

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
                URL.name == None,
                URL.description == None,
                URLOptionalDataSourceMetadata.url_id == None
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
