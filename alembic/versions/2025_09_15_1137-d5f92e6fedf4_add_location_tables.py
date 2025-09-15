"""Add Location tables

Revision ID: d5f92e6fedf4
Revises: e7189dc92a83
Create Date: 2025-09-15 11:37:58.183674

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5f92e6fedf4'
down_revision: Union[str, None] = 'e7189dc92a83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

US_STATES_TABLE_NAME = 'us_states'
COUNTIES_TABLE_NAME = 'counties'
LOCALITIES_TABLE_NAME = 'localities'
LOCATIONS_TABLE_NAME = 'locations'
LINK_AGENCIES_LOCATIONS_TABLE_NAME = 'link_agencies_locations'

def upgrade() -> None:
    _create_location_type()
    _create_us_states_table()
    _create_counties_table()
    _create_localities_table()
    _create_locations_table()
    _create_link_agencies_locations_table()

def downgrade() -> None:
    _remove_link_agencies_locations_table()
    _remove_locations_table()
    _remove_localities_table()
    _remove_counties_table()
    _remove_us_states_table()
    _remove_location_type()

def _create_location_type():
    op.execute("""
    create type location_type as enum ('National', 'State', 'County', 'Locality')
    """)

def _remove_location_type():
    op.execute("""
    drop type location_type
    """)

def _create_us_states_table():
    op.execute("""
    create table if not exists public.us_states
    (
        state_iso  text not null
            constraint unique_state_iso
                unique,
        state_name text,
        id         bigint generated always as identity
            primary key
    )
    """)

def _create_counties_table():
    op.execute("""
    create table if not exists public.counties
    (
        fips                          varchar not null
            constraint unique_fips
                unique,
        name                          text,
        lat                           double precision,
        lng                           double precision,
        population                    bigint,
        agencies                      text,
        id                            bigint generated always as identity
            primary key,
        state_id                      integer
            references public.us_states,
        unique (fips, state_id),
        constraint unique_county_name_and_state
            unique (name, state_id)
    )
    """)

def _create_localities_table():
    op.execute("""
    create table if not exists public.localities
    (
        id        bigint generated always as identity
            primary key,
        name      varchar(255) not null
            constraint localities_name_check
                check ((name)::text !~~ '%,%'::text),
        county_id integer      not null
            references public.counties,
        unique (name, county_id)
    )
    
    """)

def _create_locations_table():
    op.execute("""
    create table if not exists public.locations
    (
        id          bigint generated always as identity
            primary key,
        type        location_type not null,
        state_id    bigint
            references public.us_states
                on delete cascade,
        county_id   bigint
            references public.counties
                on delete cascade,
        locality_id bigint
            references public.localities
                on delete cascade,
        lat         double precision,
        lng         double precision,
        unique (id, type, state_id, county_id, locality_id),
        constraint locations_check
            check (((type = 'National'::location_type) AND (state_id IS NULL) AND (county_id IS NULL) AND
                    (locality_id IS NULL)) OR
                   ((type = 'State'::location_type) AND (county_id IS NULL) AND (locality_id IS NULL)) OR
                   ((type = 'County'::location_type) AND (county_id IS NOT NULL) AND (locality_id IS NULL)) OR
                   ((type = 'Locality'::location_type) AND (county_id IS NOT NULL) AND (locality_id IS NOT NULL)))
    )
    """)

def _create_link_agencies_locations_table():
    op.execute("""
    create table if not exists public.link_agencies_locations
    (
        id          serial
            primary key,
        agency_id   integer not null
            references public.agencies
                on delete cascade,
        location_id integer not null
            references public.locations
                on delete cascade,
        constraint unique_agency_location
            unique (agency_id, location_id)
    )
    """)

def _remove_link_agencies_locations_table():
    op.drop_table(LINK_AGENCIES_LOCATIONS_TABLE_NAME)

def _remove_locations_table():
    op.drop_table(LOCATIONS_TABLE_NAME)

def _remove_localities_table():
    op.drop_table(LOCALITIES_TABLE_NAME)

def _remove_counties_table():
    op.drop_table(COUNTIES_TABLE_NAME)

def _remove_us_states_table():
    op.drop_table(US_STATES_TABLE_NAME)
