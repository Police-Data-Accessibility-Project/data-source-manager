from sqlalchemy import select, exists, Column, CTE

from src.db.enums import TaskType
from src.db.helpers.query import no_url_task_error
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.link.url_agency.sqlalchemy import LinkURLAgency
from src.db.models.impl.url.core.sqlalchemy import URL
from src.db.models.impl.url.ds_meta_url.sqlalchemy import DSAppLinkMetaURL
from src.db.models.views.meta_url import MetaURL


class SubmitMetaURLsPrerequisitesCTEContainer:

    def __init__(self):

        self._cte = (
            select(
                URL.id.label("url_id"),
                URL.full_url.label("url"),
                LinkURLAgency.agency_id,
            )
            # Validated as Meta URL
            .join(
                MetaURL,
                MetaURL.url_id == URL.id
            )
            .join(
                LinkURLAgency,
                LinkURLAgency.url_id == URL.id
            )
            # Does not have a submission
            .where(
                ~exists(
                    select(
                        DSAppLinkMetaURL.ds_meta_url_id
                    )
                    .where(
                        DSAppLinkMetaURL.url_id == URL.id,
                        DSAppLinkMetaURL.agency_id == LinkURLAgency.agency_id
                    )
                ),
                no_url_task_error(TaskType.SUBMIT_META_URLS)
            )
            .cte("submit_meta_urls_prerequisites")
        )

    @property
    def cte(self) -> CTE:
        return self._cte

    @property
    def url_id(self) -> Column[int]:
        return self._cte.c.url_id

    @property
    def agency_id(self) -> Column[int]:
        return self._cte.c.agency_id

    @property
    def url(self) -> Column[str]:
        return self._cte.c.url