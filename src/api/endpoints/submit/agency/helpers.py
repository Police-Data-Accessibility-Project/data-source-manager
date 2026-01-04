from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import aggregate_order_by

from src.api.endpoints.submit.agency.request import SubmitAgencyRequestModel
from src.db.models.impl.agency.sqlalchemy import Agency
from src.db.models.impl.link.agency_location.sqlalchemy import LinkAgencyLocation
from src.db.models.impl.proposals.agency_.core import ProposalAgency
from src.db.models.impl.proposals.agency_.link__location import ProposalLinkAgencyLocation


def norm_name(col):
    # POSTGRES: lower(regexp_replace(trim(name), '\s+', ' ', 'g'))
    return func.lower(
        func.regexp_replace(func.trim(col), r"\s+", " ", "g")
    )

def exact_duplicates_for_approved_agency_query(
    request: SubmitAgencyRequestModel,
):
    link = LinkAgencyLocation
    agencies = Agency

    agency_locations_cte = (
        select(
            link.agency_id,
            # Postgres ARRAY_AGG with deterministic ordering
            func.array_agg(
                aggregate_order_by(
                    link.location_id,
                    link.location_id.asc()
                )
            ).label("location_ids")
        )
        .group_by(
            link.agency_id,
        )
        .cte("agency_locations")
    )

    query = (
        select(
            agencies.id,
        )
        .join(
            agency_locations_cte,
            agency_locations_cte.c.agency_id == agencies.id
        )
        .where(
            norm_name(agencies.name) == request.name.lower().strip(),
            agencies.jurisdiction_type == request.jurisdiction_type,
            agencies.agency_type == request.agency_type,
            agency_locations_cte.c.location_ids == sorted(request.location_ids),
        )
        .group_by(
            agencies.id,
        )
    )

    return query


def exact_duplicates_for_proposal_agency_query(
    request: SubmitAgencyRequestModel,
):
    link = ProposalLinkAgencyLocation
    agencies = ProposalAgency

    agency_locations_cte = (
        select(
            link.proposal_agency_id,
            # Postgres ARRAY_AGG with deterministic ordering
            func.array_agg(
                aggregate_order_by(
                    link.location_id,
                    link.location_id.asc()
                )
            ).label("location_ids")
        )
        .group_by(
            link.proposal_agency_id,
        )
        .cte("agency_locations")
    )

    query = (
        select(
            agencies.id,
        )
        .join(
            agency_locations_cte,
            agency_locations_cte.c.proposal_agency_id == agencies.id
        )
        .where(
            norm_name(agencies.name) == request.name.lower().strip(),
            agencies.jurisdiction_type == request.jurisdiction_type,
            agencies.agency_type == request.agency_type,
            agency_locations_cte.c.location_ids == sorted(request.location_ids),
        )
        .group_by(
            agencies.id,
        )
    )

    return query


