"""Add html duplicate url materialized view

Revision ID: d5f0cc2be6b6
Revises: 5ac9d50b91c5
Create Date: 2025-11-27 09:07:28.767553

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd5f0cc2be6b6'
down_revision: Union[str, None] = '5ac9d50b91c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
    create extension if not exists pgcrypto;
    """)

    op.execute("""
        CREATE MATERIALIZED VIEW mat_view__html_duplicate_url AS
        WITH
        hashes AS (
            SELECT
                url_id,
                digest(compressed_html, 'sha256') AS hash
            FROM
                url_compressed_html
            )
        , duplicate_hashes as (
                SELECT
                    hash AS content_hash,
                    COUNT(*) AS n,
                    ARRAY_AGG(url_id ORDER BY url_id) AS url_ids
                FROM
                    hashes
                GROUP BY
                    hash
                HAVING
                    COUNT(*) > 1
        )
        select
            urls.id as url_id
        from urls
        join hashes h on h.url_id = urls.id
        join duplicate_hashes dh on dh.content_hash = h.hash;
    """)


def downgrade() -> None:
    pass
