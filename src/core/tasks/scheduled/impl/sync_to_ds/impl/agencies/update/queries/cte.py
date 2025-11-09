from sqlalchemy import select, Column, CTE

from src.db.models.impl.agency.ds_link.sqlalchemy import DSAppLinkAgency
from src.db.models.impl.agency.sqlalchemy import Agency


class DSAppLinkSyncAgencyUpdatePrerequisitesCTEContainer:

    def __init__(self):
        self._cte = (
            select(
                DSAppLinkAgency.agency_id,
                DSAppLinkAgency.ds_agency_id,
            )
            .join(
                Agency,
                Agency.id == DSAppLinkAgency.agency_id,
            )
            .where(
                Agency.updated_at > DSAppLinkAgency.last_synced_at
            ).cte()
        )

    @property
    def ds_agency_id(self) -> Column[int]:
        return self._cte.columns.ds_agency_id

    @property
    def agency_id(self) -> Column[int]:
        return self._cte.columns.agency_id

    @property
    def cte(self) -> CTE:
        return self._cte