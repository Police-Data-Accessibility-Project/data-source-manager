"""Update locations expanded view

Revision ID: d4c63e23d3f0
Revises: b9317c6836e7
Create Date: 2025-09-26 17:51:41.214287

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

from src.util.alembic_helpers import id_column, location_id_column, created_at_column

# revision identifiers, used by Alembic.
revision: str = 'd4c63e23d3f0'
down_revision: Union[str, None] = 'b9317c6836e7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _update_locations_expanded_view():
    op.execute(
        """
        CREATE OR REPLACE VIEW locations_expanded as
        SELECT locations.id,
               locations.type,
               us_states.state_name,
               us_states.state_iso,
               counties.name   AS county_name,
               counties.fips   AS county_fips,
               localities.name AS locality_name,
               localities.id   AS locality_id,
               us_states.id    AS state_id,
               counties.id     AS county_id,
               CASE
                   WHEN locations.type = 'Locality'::location_type THEN localities.name
                   WHEN locations.type = 'County'::location_type THEN counties.name::character varying
                   WHEN locations.type = 'State'::location_type THEN us_states.state_name::character varying
                   ELSE NULL::character varying
                   END         AS display_name,
               CASE
                   WHEN locations.type = 'Locality'::location_type THEN concat(localities.name, ', ', counties.name,
                                                                               ', ',
                                                                               us_states.state_name)::character varying
                   WHEN locations.type = 'County'::location_type
                       THEN concat(counties.name, ', ', us_states.state_name)::character varying
                   WHEN locations.type = 'State'::location_type THEN us_states.state_name::character varying
                   WHEN locations.type = 'National'::location_type THEN 'United States'
                   ELSE NULL::character varying
                   END         AS full_display_name
        FROM locations
                 LEFT JOIN us_states
                           ON locations.state_id = us_states.id
                 LEFT JOIN counties
                           ON locations.county_id = counties.id
                 LEFT JOIN localities
                           ON locations.locality_id = localities.id
        """
    )


def _create_new_agency_suggestion_table():
    op.create_table(
        'new_agency_suggestions',
        id_column(),
        location_id_column(),
        sa.Column('name', sa.String()),
        sa.Column('jurisdiction_type', ENUM(name='jurisdiction_type_enum', create_type=False), nullable=True),
        sa.Column('agency_type', ENUM(name='agency_type_enum', create_type=False), nullable=True),
        created_at_column()
    )


def upgrade() -> None:
    _update_locations_expanded_view()
    _create_new_agency_suggestion_table()




def downgrade() -> None:
    pass
