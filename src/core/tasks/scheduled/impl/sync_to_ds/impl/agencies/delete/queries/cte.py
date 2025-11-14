"""
Agencies to be deleted from the DS database must be flagged for deletion
"""
from sqlalchemy import select, Column, CTE

from src.db.models.impl.agency.ds_link.sqlalchemy import DSAppLinkAgency
from src.db.models.impl.flag.ds_delete.agency import FlagDSDeleteAgency


class DSAppLinkSyncAgencyDeletePrerequisitesCTEContainer:

    def __init__(self):
        self._cte = (
            select(
                DSAppLinkAgency.ds_agency_id
            )
            .join(
                FlagDSDeleteAgency,
                FlagDSDeleteAgency.ds_agency_id == DSAppLinkAgency.ds_agency_id
            ).cte("ds_app_link_sync_agency_delete_prerequisites")
        )

    @property
    def ds_agency_id(self) -> Column[int]:
        return self._cte.columns.ds_agency_id

    @property
    def cte(self) -> CTE:
        return self._cte