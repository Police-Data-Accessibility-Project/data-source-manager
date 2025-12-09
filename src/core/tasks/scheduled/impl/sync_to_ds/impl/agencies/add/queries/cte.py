"""
Agencies to be added to the DS database must not have a
ds app link entry
"""
from sqlalchemy import Column, select, exists, CTE

from src.db.models.impl.agency.ds_link.sqlalchemy import DSAppLinkAgency
from src.db.models.impl.agency.sqlalchemy import Agency


class DSAppLinkSyncAgencyAddPrerequisitesCTEContainer:

    def __init__(self):
        self._cte = (
            select(
                Agency.id
            )
            .where(
                ~exists(
                    select(DSAppLinkAgency.agency_id)
                    .where(DSAppLinkAgency.agency_id == Agency.id)
                )
            ).cte("ds_app_link_sync_agency_add_prerequisites")
        )

    @property
    def agency_id(self) -> Column[int]:
        return self._cte.columns.id

    @property
    def cte(self) -> CTE:
        return self._cte