from sqlalchemy import select, literal, Exists, Label, or_

from src.db.models.templates_.base import Base
from src.db.models.views.integrity.incomplete_data_sources import IntegrityIncompleteDataSource
from src.db.models.views.integrity.incomplete_meta_urls import IntegrityIncompleteMetaURL
from src.db.models.views.integrity.non_federal_agencies_no_location import IntegrityNonFederalAgenciesNoLocation
from src.db.models.views.integrity.url_both_data_source_and_meta_url import IntegrityURLBothDataSourceAndMetaURL


def any_row_exists(
    model: type[Base]
) -> Exists:
    return (
        select(
            literal(1)
        )
        .select_from(
            model
        )
        .exists()
    )

class IntegrityTaskCTEContainer:

    def __init__(
        self,
    ):
        self.models: list[type[Base]] = [
            IntegrityURLBothDataSourceAndMetaURL,
            IntegrityNonFederalAgenciesNoLocation,
            IntegrityIncompleteMetaURL,
            IntegrityIncompleteDataSource,
        ]

        expressions: list[Label[bool]] = [
            any_row_exists(model)
            .label(model.__tablename__)
            for model in self.models
        ]

        self.cte = (
            select(
                *expressions
            )
            .cte(
                name="integrity_task_cte",
            )
        )

    @property
    def any_rows_exist_query(self) -> select:
        expression = [
            getattr(self.cte.c, model.__tablename__)
            for model in self.models
        ]
        return select(or_(*expression))

    @property
    def select_all_columns_query(self) -> select:
        return select(self.cte)

