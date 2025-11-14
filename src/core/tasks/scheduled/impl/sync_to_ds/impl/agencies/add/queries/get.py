from typing import Sequence

from sqlalchemy import select, RowMapping, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.tasks.scheduled.impl.sync_to_ds.impl.agencies.add.queries.cte import \
    DSAppLinkSyncAgencyAddPrerequisitesCTEContainer
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.link.agency_location.sqlalchemy import LinkAgencyLocation
from src.db.queries.base.builder import QueryBuilderBase
from src.external.pdap.impl.sync.agencies._shared.models.content import AgencySyncContentModel
from src.external.pdap.impl.sync.agencies.add.request import AddAgenciesOuterRequest, AddAgenciesInnerRequest


class DSAppSyncAgenciesAddGetQueryBuilder(QueryBuilderBase):

    async def run(self, session: AsyncSession) -> AddAgenciesOuterRequest:
        cte = DSAppLinkSyncAgencyAddPrerequisitesCTEContainer()

        location_id_cte = (
            select(
                LinkAgencyLocation.agency_id,
                func.array_agg(LinkAgencyLocation.location_id).label("location_ids"),
            )
            .group_by(
                LinkAgencyLocation.agency_id,
            )
            .cte("location_id_cte")
        )

        query = (
            select(
                cte.agency_id,
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
        )

        mappings: Sequence[RowMapping] = await self.sh.mappings(
            session=session,
            query=query,
        )

        inner_requests: list[AddAgenciesInnerRequest] = []
        for mapping in mappings:
            inner_requests.append(
                AddAgenciesInnerRequest(
                    request_id=mapping[cte.agency_id],
                    content=AgencySyncContentModel(
                        name=mapping[Agency.name],
                        jurisdiction_type=mapping[Agency.jurisdiction_type],
                        agency_type=mapping[Agency.agency_type],
                        location_ids=mapping["location_ids"]
                    )
                )
            )

        return AddAgenciesOuterRequest(
            agencies=inner_requests,
        )