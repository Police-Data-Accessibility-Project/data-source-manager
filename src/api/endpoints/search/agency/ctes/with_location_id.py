from sqlalchemy import select, literal, CTE, Column

from src.db.models.impl.link.agency_location.sqlalchemy import LinkAgencyLocation
from src.db.models.views.dependent_locations import DependentLocationView


class WithLocationIdCTEContainer:

    def __init__(self, location_id: int):

        target_locations_cte = (
            select(
                literal(location_id).label("location_id")
            )
            .union(
                select(
                    DependentLocationView.dependent_location_id
                )
                .where(
                    DependentLocationView.parent_location_id == location_id
                )
            )
            .cte("target_locations")
        )

        self._cte = (
            select(
                LinkAgencyLocation.agency_id,
                LinkAgencyLocation.location_id
            )
            .join(
                target_locations_cte,
                target_locations_cte.c.location_id == LinkAgencyLocation.location_id
            )
            .cte("with_location_id")
        )

    @property
    def cte(self) -> CTE:
        return self._cte

    @property
    def agency_id(self) -> Column:
        return self._cte.c.agency_id

    @property
    def location_id(self) -> Column:
        return self._cte.c.location_id