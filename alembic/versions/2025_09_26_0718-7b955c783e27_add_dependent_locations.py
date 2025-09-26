"""Add dependent locations

Revision ID: 7b955c783e27
Revises: 3687026267fc
Create Date: 2025-09-26 07:18:37.916841

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b955c783e27'
down_revision: Union[str, None] = '3687026267fc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        create view dependent_locations(parent_location_id, dependent_location_id) as
    SELECT
        lp.id AS parent_location_id,
        ld.id AS dependent_location_id
    FROM
        locations lp
            JOIN locations ld ON ld.state_id = lp.state_id AND ld.type = 'County'::location_type AND lp.type = 'State'::location_type
    UNION ALL
    SELECT
        lp.id AS parent_location_id,
        ld.id AS dependent_location_id
    FROM
        locations lp
            JOIN locations ld ON ld.county_id = lp.county_id AND ld.type = 'Locality'::location_type AND lp.type = 'County'::location_type
    UNION ALL
    SELECT
        lp.id AS parent_location_id,
        ld.id AS dependent_location_id
    FROM
        locations lp
            JOIN locations ld ON ld.state_id = lp.state_id AND ld.type = 'Locality'::location_type AND lp.type = 'State'::location_type
    UNION ALL
    SELECT
        lp.id AS parent_location_id,
        ld.id AS dependent_location_id
    FROM
        locations lp
            JOIN locations ld ON lp.type = 'National'::location_type AND (ld.type = ANY
                                                                          (ARRAY ['State'::location_type, 'County'::location_type, 'Locality'::location_type]))
    """)


def downgrade() -> None:
    pass
