from typing import Sequence

from sqlalchemy import select, func, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync_to_ds.constants import PER_REQUEST_ENTITY_LIMIT
from src.core.tasks.scheduled.impl.sync_to_ds.impl.agencies.update.queries.cte import \
    DSAppLinkSyncAgencyUpdatePrerequisitesCTEContainer
from src.db.models.impl.agency.ds_link.sqlalchemy import DSAppLinkAgency
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.link.agency_location.sqlalchemy import LinkAgencyLocation
from src.db.queries.base.builder import QueryBuilderBase
from src.external.pdap.impl.sync.agencies._shared.models.content import AgencySyncContentModel
from src.external.pdap.impl.sync.agencies.update.request import UpdateAgenciesOuterRequest, UpdateAgenciesInnerRequest


class DSAppSyncAgenciesUpdateGetQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> UpdateAgenciesOuterRequest:
        cte = DSAppLinkSyncAgencyUpdatePrerequisitesCTEContainer()

        location_id_cte = (
            select(
                LinkAgencyLocation.agency_id,
                func.array_agg(LinkAgencyLocation.location_id).label("location_ids"),
            )
            .join(
                Agency,
                Agency.id == LinkAgencyLocation.agency_id,
            )
            .group_by(
                LinkAgencyLocation.agency_id,
            )
            .cte()
        )

        query = (
            select(
                cte.ds_agency_id,
                Agency.name,
                Agency.jurisdiction_type,
                Agency.agency_type,
                location_id_cte.c.location_ids,
            )
            .join(
                Agency,
                Agency.id == cte.agency_id,
            )
            .join(
                location_id_cte,
                location_id_cte.c.agency_id == cte.agency_id,
            )
            .limit(PER_REQUEST_ENTITY_LIMIT)
        )

        mappings: Sequence[RowMapping] = await self.sh.mappings(
            session=session,
            query=query,
        )

        inner_requests: list[UpdateAgenciesInnerRequest] = []
        for mapping in mappings:
            inner_requests.append(
                UpdateAgenciesInnerRequest(
                    app_id=mapping[cte.ds_agency_id],
                    content=AgencySyncContentModel(
                        name=mapping[Agency.name],
                        jurisdiction_type=mapping[Agency.jurisdiction_type],
                        agency_type=mapping[Agency.agency_type],
                        location_ids=mapping["location_ids"]
                    )
                )
            )

        return UpdateAgenciesOuterRequest(
            agencies=inner_requests,
        )