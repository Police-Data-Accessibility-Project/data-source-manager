"""Add federal agency location integrity check

Revision ID: c2f46d1af640
Revises: 1fb2286a016c
Create Date: 2026-02-27 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'c2f46d1af640'
down_revision: Union[str, None] = '1fb2286a016c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    _create_federal_agencies_wrong_location_view()
    _normalize_federal_agency_locations()


def _create_federal_agencies_wrong_location_view() -> None:
    op.execute("""
    create view integrity__federal_agencies_wrong_location_view as
        with national_location as (
            select id
            from locations
            where type = 'National'::location_type
            limit 1
        )
        select
            ag.id as agency_id
        from agencies ag
        inner join link_agencies__locations link on ag.id = link.agency_id
        cross join national_location nl
        where ag.jurisdiction_type = 'federal'
        group by ag.id, nl.id
        having array_agg(link.location_id order by link.location_id) != array[nl.id::integer]
    """)


def _normalize_federal_agency_locations() -> None:
    op.execute("""
    with national_location as (
        select id
        from locations
        where type = 'National'::location_type
        limit 1
    )
    delete from link_agencies__locations link
    using agencies ag, national_location nl
    where link.agency_id = ag.id
      and ag.jurisdiction_type = 'federal'
      and link.location_id != nl.id::integer
    """)

    op.execute("""
    with national_location as (
        select id
        from locations
        where type = 'National'::location_type
        limit 1
    )
    insert into link_agencies__locations (agency_id, location_id)
    select
        ag.id,
        nl.id::integer
    from agencies ag
    cross join national_location nl
    left join link_agencies__locations link
        on link.agency_id = ag.id
        and link.location_id = nl.id::integer
    where ag.jurisdiction_type = 'federal'
      and link.agency_id is null
    """)


def downgrade() -> None:
    op.execute("drop view if exists integrity__federal_agencies_wrong_location_view")
